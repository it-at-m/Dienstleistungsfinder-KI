export type CollectionName = "service" | "info";

export type CollectionSelection = "all" | CollectionName[];

export type RetrievalResultType = "minimal" | "full";

export type CategoryMatchStrategy = "any" | "all";

export default interface RetrievalInput {
  query: string;
  keywords?: string[];
  categories?: string[];
  run_id?: string;
  result: RetrievalResultType;
  collections: CollectionSelection;
  category_match: CategoryMatchStrategy;
  rerank: boolean;
}
