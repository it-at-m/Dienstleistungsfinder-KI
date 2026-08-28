export interface RetrievedDocumentBase {
  id: string;
  name: string;
  collection: string;
  kind: "minimal" | "full";
}

export interface RetrievedDocumentMinimal extends RetrievedDocumentBase {
  kind: "minimal";
}

export interface RetrievedDocumentFull extends RetrievedDocumentBase {
  kind: "full";
  page_content: string;
  metadata: Record<string, unknown>;
}

export type RetrievedDocument =
  RetrievedDocumentMinimal | RetrievedDocumentFull;

export interface EnhancedQuery {
  query: string;
  was_enhanced: boolean;
}

export default interface RetrievalResult {
  run_id: string;
  retrieval_documents: RetrievedDocument[];
  enhanced_query: EnhancedQuery;
}
