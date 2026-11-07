# Canonical PES 2013 dt04.img — status

This manifest records the canonical binary identified in the forensic workspace.

- Canonical filename: `dt04.img`
- Length: `10,121,216` bytes
- SHA-256: `edf4ba7651b66e8fe8ab158c8bbc43b0d7ae7838e4b60b4457976c51698d248e`
- Git blob SHA-1 for the canonical bytes: `18ac644fca5c0f008eb288e28ce9c657686d2c54`
- Source filename received for this canonical artifact: `dt04(1).img`

## Important: binary replacement is still pending

The existing root-level `dt04.img` in this repository is **not** confirmed to be the canonical file above. Its current Git blob SHA was observed as:

- Repository `BartVasco11/peseditor`: `ee4a24f61eedc79b2bbc7c772314526eea19a280`
- Repository `BartVasco11/PES-programs5`: `433de9e95856cfab3c543d616b1263df69024834`

Both differ from the canonical Git blob SHA. Do not treat either existing binary as canonical. No binary was overwritten by this manifest update.

The canonical binary must replace the root-level `dt04.img` only after an exact byte upload and post-upload SHA-256 verification. Until then, this manifest is the source-of-truth checksum record, not the binary itself.
