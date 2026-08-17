export interface MailtoTemplateConfig {
  to: string;
  subject: string;
  /**
   * Base body that will be followed by the run_id/query context so operators can connect responses to a search.
   */
  body: string;
}

export interface FeedbackConfig {
  positive: MailtoTemplateConfig;
  negative: MailtoTemplateConfig;
}
