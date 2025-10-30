import Image from '@/components/image';
import SvgIcon from '@/components/svg-icon';
import { IReference, IReferenceChunk } from '@/interfaces/database/chat';
import { getExtension } from '@/utils/document-util';
import { InfoCircleOutlined } from '@ant-design/icons';
import { Button, Flex, Popover } from 'antd';
import DOMPurify from 'dompurify';
import { useCallback, useEffect, useMemo } from 'react';
import Markdown from 'react-markdown';
import reactStringReplace from 'react-string-replace';
import SyntaxHighlighter from 'react-syntax-highlighter';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { visitParents } from 'unist-util-visit-parents';

import { useFetchDocumentThumbnailsByIds } from '@/hooks/document-hooks';
import { useTranslation } from 'react-i18next';

import 'katex/dist/katex.min.css'; // `rehype-katex` does not import the CSS for you

import {
  preprocessLaTeX,
  replaceThinkToSection,
  showImage,
} from '@/utils/chat';
import { currentReg, replaceTextByOldReg } from '../utils';

import classNames from 'classnames';
import { omit } from 'lodash';
import { pipe } from 'lodash/fp';
import styles from './index.less';

const getChunkIndex = (match: string) => Number(match);
// TODO: The display of the table is inconsistent with the display previously placed in the MessageItem.
const MarkdownContent = ({
  reference,
  clickDocumentButton,
  content,
}: {
  content: string;
  loading: boolean;
  reference: IReference;
  clickDocumentButton?: (documentId: string, chunk: IReferenceChunk) => void;
}) => {
  const { t } = useTranslation();
  const { setDocumentIds, data: fileThumbnails } =
    useFetchDocumentThumbnailsByIds();
  const contentWithCursor = useMemo(() => {
    // let text = DOMPurify.sanitize(content);
    let text = content;
    if (text === '') {
      text = t('chat.searching');
    }
    const nextText = replaceTextByOldReg(text);
    return pipe(replaceThinkToSection, preprocessLaTeX)(nextText);
  }, [content, t]);

  useEffect(() => {
    const docAggs = reference?.doc_aggs;
    setDocumentIds(Array.isArray(docAggs) ? docAggs.map((x) => x.doc_id) : []);
  }, [reference, setDocumentIds]);

  const handleDocumentButtonClick = useCallback(
    (
      documentId: string,
      chunk: IReferenceChunk,
      isPdf: boolean,
      documentUrl?: string,
    ) =>
      () => {
        if (!isPdf) {
          if (!documentUrl) {
            return;
          }
          window.open(documentUrl, '_blank');
        } else {
          clickDocumentButton?.(documentId, chunk);
        }
      },
    [clickDocumentButton],
  );

  const rehypeWrapReference = () => {
    return function wrapTextTransform(tree: any) {
      visitParents(tree, 'text', (node, ancestors) => {
        const latestAncestor = ancestors.at(-1);
        if (
          latestAncestor.tagName !== 'custom-typography' &&
          latestAncestor.tagName !== 'code'
        ) {
          node.type = 'element';
          node.tagName = 'custom-typography';
          node.properties = {};
          node.children = [{ type: 'text', value: node.value }];
        }
      });
    };
  };

  const getReferenceInfo = useCallback(
    (chunkIndex: number) => {
      const chunks = reference?.chunks ?? [];
      const chunkItem = chunks[chunkIndex];
      const document = reference?.doc_aggs?.find(
        (x) => x?.doc_id === chunkItem?.document_id,
      );
      const documentId = document?.doc_id;
      const documentUrl = document?.url;
      const fileThumbnail = documentId ? fileThumbnails[documentId] : '';
      const fileExtension = documentId ? getExtension(document?.doc_name) : '';
      const imageId = chunkItem?.image_id;

      return {
        documentUrl,
        fileThumbnail,
        fileExtension,
        imageId,
        chunkItem,
        documentId,
        document,
      };
    },
    [fileThumbnails, reference],
  );

  const getPopoverContent = useCallback(
    (chunkIndex: number) => {
      const {
        documentUrl,
        fileThumbnail,
        fileExtension,
        imageId,
        chunkItem,
        documentId,
        document,
      } = getReferenceInfo(chunkIndex);

      return (
        <div key={chunkItem?.id} className="flex gap-2">
          {imageId && (
            <Popover
              placement="left"
              content={
                <Image
                  id={imageId}
                  className={styles.referenceImagePreview}
                ></Image>
              }
            >
              <Image
                id={imageId}
                className={styles.referenceChunkImage}
              ></Image>
            </Popover>
          )}
          <div className={'space-y-2 max-w-[40vw]'}>
            <div
              dangerouslySetInnerHTML={{
                __html: DOMPurify.sanitize(chunkItem?.content ?? ''),
              }}
              className={classNames(styles.chunkContentText)}
            ></div>
            {documentId && (
              <Flex gap={'small'}>
                {fileThumbnail ? (
                  <img
                    src={fileThumbnail}
                    alt=""
                    className={styles.fileThumbnail}
                  />
                ) : (
                  <SvgIcon
                    name={`file-icon/${fileExtension}`}
                    width={24}
                  ></SvgIcon>
                )}
                <Button
                  type="link"
                  className={classNames(styles.documentLink, 'text-wrap')}
                  onClick={handleDocumentButtonClick(
                    documentId,
                    chunkItem,
                    fileExtension === 'pdf',
                    documentUrl,
                  )}
                >
                  {document?.doc_name}
                </Button>
              </Flex>
            )}
          </div>
        </div>
      );
    },
    [getReferenceInfo, handleDocumentButtonClick],
  );

  const renderReference = useCallback(
    (text: string) => {
      let replacedText = reactStringReplace(text, currentReg, (match, i) => {
        const chunkIndex = getChunkIndex(match);

        const { documentUrl, fileExtension, imageId, chunkItem, documentId } =
          getReferenceInfo(chunkIndex);

        const docType = chunkItem?.doc_type;

        return showImage(docType) ? (
          <Image
            id={imageId}
            className={styles.referenceInnerChunkImage}
            onClick={
              documentId
                ? handleDocumentButtonClick(
                    documentId,
                    chunkItem,
                    fileExtension === 'pdf',
                    documentUrl,
                  )
                : () => {}
            }
          ></Image>
        ) : (
          <Popover content={getPopoverContent(chunkIndex)} key={i}>
            <InfoCircleOutlined className={styles.referenceIcon} />
          </Popover>
        );
      });

      // replacedText = reactStringReplace(replacedText, curReg, (match, i) => (
      //   <span className={styles.cursor} key={i}></span>
      // ));

      return replacedText;
    },
    [getPopoverContent, getReferenceInfo, handleDocumentButtonClick],
  );

  return (
    <Markdown
      rehypePlugins={[rehypeWrapReference, rehypeKatex, rehypeRaw]}
      remarkPlugins={[remarkGfm, remarkMath]}
      className={styles.markdownContentWrapper}
      components={
        {
          'custom-typography': ({ children }: { children: string }) =>
            renderReference(children),
          // Enhanced list formatting with professional styling
          ol: ({ children, ...props }: any) => (
            <ol 
              {...props} 
              className="list-decimal list-inside space-y-2 ml-4 my-4"
              style={{ 
                counterReset: 'item',
                paddingLeft: '1.5rem'
              }}
            >
              {children}
            </ol>
          ),
          ul: ({ children, ...props }: any) => (
            <ul 
              {...props} 
              className="list-disc list-inside space-y-2 ml-4 my-4"
              style={{ paddingLeft: '1.5rem' }}
            >
              {children}
            </ul>
          ),
          li: ({ children, ...props }: any) => (
            <li 
              {...props} 
              className="mb-2 leading-relaxed"
              style={{ 
                display: 'list-item',
                marginBottom: '0.5rem',
                lineHeight: '1.6'
              }}
            >
              {children}
            </li>
          ),
          // Enhanced paragraph formatting
          p: ({ children, ...props }: any) => (
            <p 
              {...props} 
              className="mb-4 leading-relaxed text-gray-800"
              style={{ 
                marginBottom: '1rem',
                lineHeight: '1.6',
                color: '#374151'
              }}
            >
              {children}
            </p>
          ),
          // Enhanced heading formatting
          h1: ({ children, ...props }: any) => (
            <h1 
              {...props} 
              className="text-2xl font-bold mb-4 text-gray-900 border-b border-gray-200 pb-2"
              style={{ 
                fontSize: '1.5rem',
                fontWeight: 'bold',
                marginBottom: '1rem',
                color: '#111827',
                borderBottom: '1px solid #e5e7eb',
                paddingBottom: '0.5rem'
              }}
            >
              {children}
            </h1>
          ),
          h2: ({ children, ...props }: any) => (
            <h2 
              {...props} 
              className="text-xl font-semibold mb-3 text-gray-800"
              style={{ 
                fontSize: '1.25rem',
                fontWeight: '600',
                marginBottom: '0.75rem',
                color: '#1f2937'
              }}
            >
              {children}
            </h2>
          ),
          h3: ({ children, ...props }: any) => (
            <h3 
              {...props} 
              className="text-lg font-medium mb-2 text-gray-700"
              style={{ 
                fontSize: '1.125rem',
                fontWeight: '500',
                marginBottom: '0.5rem',
                color: '#374151'
              }}
            >
              {children}
            </h3>
          ),
          // Enhanced blockquote for source citations
          blockquote: ({ children, ...props }: any) => (
            <blockquote 
              {...props} 
              className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 rounded-r"
              style={{ 
                borderLeft: '4px solid #3b82f6',
                paddingLeft: '1rem',
                paddingTop: '0.5rem',
                paddingBottom: '0.5rem',
                marginTop: '1rem',
                marginBottom: '1rem',
                backgroundColor: '#eff6ff',
                borderRadius: '0 0.375rem 0.375rem 0'
              }}
            >
              {children}
            </blockquote>
          ),
          // Enhanced code formatting
          code(props: any) {
            const { children, className, ...rest } = props;
            const restProps = omit(rest, 'node');
            const match = /language-(\w+)/.exec(className || '');
            return match ? (
              <SyntaxHighlighter
                {...restProps}
                PreTag="div"
                language={match[1]}
                wrapLongLines
                className="rounded-lg shadow-sm"
                style={{
                  borderRadius: '0.5rem',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                }}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code
                {...restProps}
                className={classNames(className, 'text-wrap bg-gray-100 px-1 py-0.5 rounded text-sm')}
                style={{
                  backgroundColor: '#f3f4f6',
                  padding: '0.125rem 0.25rem',
                  borderRadius: '0.25rem',
                  fontSize: '0.875rem'
                }}
              >
                {children}
              </code>
            );
          },
          // Enhanced table formatting
          table: ({ children, ...props }: any) => (
            <div className="overflow-x-auto my-4">
              <table 
                {...props} 
                className="min-w-full border-collapse border border-gray-300 rounded-lg shadow-sm"
                style={{
                  minWidth: '100%',
                  borderCollapse: 'collapse',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.5rem',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                }}
              >
                {children}
              </table>
            </div>
          ),
          thead: ({ children, ...props }: any) => (
            <thead 
              {...props} 
              className="bg-gray-50"
              style={{ backgroundColor: '#f9fafb' }}
            >
              {children}
            </thead>
          ),
          th: ({ children, ...props }: any) => (
            <th 
              {...props} 
              className="px-4 py-2 text-left font-semibold text-gray-700 border-b border-gray-300"
              style={{
                padding: '0.5rem 1rem',
                textAlign: 'left',
                fontWeight: '600',
                color: '#374151',
                borderBottom: '1px solid #d1d5db'
              }}
            >
              {children}
            </th>
          ),
          td: ({ children, ...props }: any) => (
            <td 
              {...props} 
              className="px-4 py-2 border-b border-gray-200"
              style={{
                padding: '0.5rem 1rem',
                borderBottom: '1px solid #e5e7eb'
              }}
            >
              {children}
            </td>
          ),
        } as any
      }
    >
      {contentWithCursor}
    </Markdown>
  );
};

export default MarkdownContent;
