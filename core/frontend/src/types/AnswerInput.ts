import type { EnhancedQuery } from "./RetrievalResult";

export interface AnswerDocument {
  id: string;
  collection: string;
}

export default interface AnswerInput {
  doc: AnswerDocument;
  enhanced_query: EnhancedQuery;
  run_id: string;
}
