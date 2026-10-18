import { createReadStream, createWriteStream } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, basename } from 'node:path';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';
import { createHash, timingSafeEqual } from 'node:crypto';
import { createInterface } from 'node:readline';
import postgres from 'postgres';

export const runtime = 'nodejs';
export const maxDuration = 300;

const STORAGE_HOST = 'br-flat-term-ads61l6c.storage.c-2.us-east-1.aws.neon.tech';
const ALLOWED_PATHS = new Set([
  '/football-rag-ingest/initial/football_chunks.jsonl',
  '/football-rag-ingest/web/web_chunks.jsonl',
]);

const hash = (value: string) =>
  createHash('sha256').update(String(value)).digest('hex');

const sourceIdFor = (type: string, uri: string) =>
  'ingest_' + hash(type + '\0' + uri).slice(0, 40);

const getSourceUri = (row: Record<string, any>) => {
  const raw = String(row.source_path || row.url || row.canonical_uri || row.source_url || ('unknown:' + row.chunk_id));
  if (/^[A-Za-z]:[\\/]/.test(raw)) {
    const parts = raw.replace(/\\/g, '/').split('/');
    return 'file:///' + parts.map((part, index) => index === 0 ? part : encodeURIComponent(part)).join('/');
  }
  if (/^file:\/\//i.test(raw)) {
    try { return new URL(raw).href; } catch { return raw; }
  }
  return raw;
};

const getSourceType = (uri: string) => {
  if (/^https?:\/\//i.test(uri)) return 'web';
  if (/\.jsonl(?:#.*)?$/i.test(uri)) return 'dataset';
  return 'file';
};

async function* readRows(file: string) {
  const lines = createInterface({
    input: createReadStream(file, { encoding: 'utf8' }),
    crlfDelay: Infinity,
  });
  let lineNo = 0;
  for await (const line of lines) {
    lineNo++;
    if (!line.trim()) continue;
    let row: Record<string, any>;
    try {
      row = JSON.parse(line);
    } catch {
      throw new Error('Invalid JSONL at line ' + lineNo);
    }
    if (!row || typeof row !== 'object' || typeof row.content !== 'string') {
      throw new Error('Invalid chunk record at line ' + lineNo);
    }
    yield row;
  }
}

function authorized(request: Request) {
  const expected = process.env.NEON_INGEST_TOKEN;
  const header = request.headers.get('authorization') || '';
  if (!expected || !header.startsWith('Bearer ')) return false;
  const suppliedBytes = Buffer.from(header.slice(7));
  const expectedBytes = Buffer.from(expected);
  return suppliedBytes.length === expectedBytes.length &&
    timingSafeEqual(suppliedBytes, expectedBytes);
}

function validateSourceUrl(value: unknown) {
  if (typeof value !== 'string') throw new Error('sourceUrl must be a string');
  const url = new URL(value);
  if (url.protocol !== 'https:' || url.hostname !== STORAGE_HOST || !ALLOWED_PATHS.has(url.pathname)) {
    throw new Error('Source URL is not an approved Neon staging object');
  }
  return url;
}

export async function POST(request: Request) {
  if (!authorized(request)) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }
  if (!process.env.NEON_DATABASE_URL) {
    return Response.json({ error: 'NEON_DATABASE_URL is not configured for this preview' }, { status: 503 });
  }

  let sourceUrl: URL;
  try {
    const body = await request.json();
    sourceUrl = validateSourceUrl(body.sourceUrl);
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : 'Invalid request' }, { status: 400 });
  }

  const tempDir = await mkdtemp(join(tmpdir(), 'neon-ingest-'));
  const file = join(tempDir, basename(sourceUrl.pathname));
  const sql = postgres(process.env.NEON_DATABASE_URL, {
    max: 4,
    idle_timeout: 20,
    connect_timeout: 20,
  });

  try {
    const response = await fetch(sourceUrl, { redirect: 'error' });
    if (!response.ok || !response.body) {
      return Response.json({ error: 'Could not download staging object', status: response.status }, { status: 502 });
    }
    await pipeline(Readable.fromWeb(response.body as any), createWriteStream(file));

    const sourceMap = new Map<string, {
      sourceId: string; type: string; uri: string; title: string;
      language: string; hash: string; extractor: string | null; metadata: Record<string, unknown>;
    }>();
    let inputCount = 0;
    for await (const row of readRows(file)) {
      inputCount++;
      const uri = getSourceUri(row);
      const type = getSourceType(uri);
      const sourceId = sourceIdFor(type, uri);
      const metadata = {
        ...(row.metadata && typeof row.metadata === 'object' ? row.metadata : {}),
        source_path: row.source_path ?? null,
        source_url: row.url ?? row.source_url ?? null,
        source_sha256: row.source_sha256 ?? null,
        ingestion_file: basename(sourceUrl.pathname),
      };
      if (!sourceMap.has(uri)) {
        sourceMap.set(uri, {
          sourceId, type, uri,
          title: row.title || basename(uri.replace(/[?#].*$/, '').replace(/\\/g, '/')) || uri,
          language: row.language || 'und',
          hash: row.source_sha256 || hash(uri),
          extractor: typeof metadata.extractor === 'string' ? metadata.extractor : null,
          metadata,
        });
      }
    }

    const existingSources = await sql.unsafe(
      'SELECT source_id, canonical_uri, source_type FROM football_rag.sources WHERE canonical_uri = ANY($1::text[])',
      [[...sourceMap.keys()]],
    );
    const existingByUri = new Map(existingSources.map((row: any) => [row.canonical_uri, row]));
    for (const [uri, source] of sourceMap) {
      const existing = existingByUri.get(uri) as any;
      if (existing) {
        source.sourceId = existing.source_id;
        source.type = existing.source_type;
      }
    }
    const resolvedSourceIds = new Map([...sourceMap].map(([uri, source]) => [uri, source.sourceId]));
    const sourceRows = [...sourceMap.values()];
    const sourceColumns = [
      'source_id','source_type','canonical_uri','title','language',
      'content_sha256','status','extractor','metadata',
    ];
    for (let i = 0; i < sourceRows.length; i += 100) {
      const batch = sourceRows.slice(i, i + 100);
      const values: any[] = [];
      const groups = batch.map((s, ri) => {
        const row = [
          s.sourceId, s.type, s.uri, s.title, s.language, s.hash,
          'chunked', s.extractor, JSON.stringify(s.metadata),
        ];
        return '(' + row.map((value, ci) => {
          values.push(value);
          return '$' + (ri * row.length + ci + 1) + (ci === 8 ? '::jsonb' : '');
        }).join(',') + ')';
      });
      await sql.unsafe(
        'INSERT INTO football_rag.sources (' + sourceColumns.join(',') + ') VALUES ' + groups.join(',') +
        ' ON CONFLICT (source_id) DO UPDATE SET source_type=EXCLUDED.source_type, canonical_uri=EXCLUDED.canonical_uri,' +
        ' title=EXCLUDED.title, language=EXCLUDED.language, content_sha256=EXCLUDED.content_sha256, status=\'chunked\',' +
        ' extractor=EXCLUDED.extractor, metadata=EXCLUDED.metadata, last_seen_at=now(), updated_at=now()',
        values,
      );
    }

    const chunkColumns = [
      'chunk_id','source_id','chunk_index','content','content_sha256','language',
      'title_path','entities','terminology','extraction_warnings','metadata','search_vector',
    ];
    let inserted = 0;
    let processed = 0;
    let batch: any[][] = [];

    const flush = async () => {
      if (!batch.length) return;
      const values: any[] = [];
      const groups = batch.map((row, ri) => '(' + row.map((value, ci) => {
        values.push(value);
        const cast = ci === 6 ? '::text[]' : ([7, 8, 9, 10].includes(ci) ? '::jsonb' : '');
        return '$' + (ri * 11 + ci + 1) + cast;
      }).join(',') + ',to_tsvector(\'simple\',$' + (ri * 11 + 4) + '))');
      const result = await sql.unsafe(
        'INSERT INTO football_rag.chunks (' + chunkColumns.join(',') + ') VALUES ' + groups.join(',') +
        ' ON CONFLICT DO NOTHING RETURNING chunk_id',
        values,
      );
      inserted += result.length;
      processed += batch.length;
      batch = [];
    };

    for await (const row of readRows(file)) {
      const uri = getSourceUri(row);
      const type = getSourceType(uri);
      const sourceId = resolvedSourceIds.get(uri) || sourceIdFor(type, uri);
      const chunkId = String(row.chunk_id || hash(sourceId + '\0' + (row.chunk_index ?? 0) + '\0' + row.content));
      batch.push([
        chunkId, sourceId, Number.isInteger(row.chunk_index) ? row.chunk_index : Number(row.chunk_index || 0),
        row.content, String(row.content_sha256 || hash(row.content)), row.language || 'und',
        Array.isArray(row.title_path) ? row.title_path : [],
        JSON.stringify(row.entities ?? []), JSON.stringify(row.terminology ?? []),
        JSON.stringify(row.extraction_warnings ?? []), JSON.stringify(row.metadata ?? {}),
      ]);
      if (batch.length >= 100) await flush();
    }
    await flush();

    const counts = await sql.unsafe(
      "SELECT 'chunks' AS table_name, count(*)::int AS total FROM football_rag.chunks UNION ALL SELECT 'sources', count(*)::int FROM football_rag.sources"
    );
    return Response.json({
      success: true,
      inputFile: basename(sourceUrl.pathname),
      validatedLines: inputCount,
      uniqueSources: sourceRows.length,
      chunksProcessed: processed,
      chunksInserted: inserted,
      chunksAlreadyPresent: processed - inserted,
      finalCounts: counts,
    });
  } catch (error) {
    console.error('Neon ingest failed:', error instanceof Error ? error.message : 'unknown error');
    return Response.json({ error: 'Ingestion failed; check preview function logs' }, { status: 500 });
  } finally {
    await sql.end({ timeout: 10 }).catch(() => {});
    await rm(tempDir, { recursive: true, force: true }).catch(() => {});
  }
}
