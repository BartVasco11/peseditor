'use client';

import { cn } from '@/lib/utils';
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { type ComponentProps, memo } from 'react';

type ResponseProps = Omit<ComponentProps<typeof ReactMarkdown>, 'components'> & {
  className?: string;
  components?: Components;
};

export const Response = memo(
  ({ className, components, ...props }: ResponseProps) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      className={cn(
        'size-full [&>*:first-child]:mt-0 [&>*:last-child]:mb-0',
        className,
      )}
      components={{
        code: ({ children, className }) => (
          <code className={className}>{children}</code>
        ),
        ...components,
      }}
      {...props}
    />
  ),
  (prevProps, nextProps) => prevProps.children === nextProps.children,
);

Response.displayName = 'Response';
