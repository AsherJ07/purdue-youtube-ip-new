import { z } from "zod";

export const formSchema = z
  .object({
    query: z.string().trim().min(1, "Enter A Niche Or Keyword."),
    timeframe: z.string(),
    custom_start: z.string().optional().default(""),
    custom_end: z.string().optional().default(""),
    match_mode: z.string(),
    region: z.string(),
    language: z.string(),
    freshness_focus: z.string(),
    duration_preference: z.string(),
    language_strictness: z.string(),
    min_views: z.coerce.number().int().min(0),
    min_subscribers: z.coerce.number().int().min(0),
    max_subscribers: z.coerce.number().int().min(0),
    include_hidden: z.boolean(),
    exclude_keywords: z.string().default(""),
    search_pages: z.coerce.number().int().min(2).max(4),
    baseline_channels: z.coerce.number().int().min(10).max(20),
    baseline_videos: z.coerce.number().int().min(10).max(30),
  })
  .superRefine((values, ctx) => {
    if (values.timeframe === "Custom") {
      if (!values.custom_start || !values.custom_end) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Choose Both Start And End Dates For A Custom Timeframe.",
          path: ["custom_start"],
        });
      }
      if (values.custom_start && values.custom_end && values.custom_start > values.custom_end) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "The Start Date Must Be On Or Before The End Date.",
          path: ["custom_end"],
        });
      }
    }

    if (values.max_subscribers > 0 && values.min_subscribers > values.max_subscribers) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Maximum Subscribers Must Be Greater Than Or Equal To Minimum Subscribers.",
        path: ["max_subscribers"],
      });
    }
  });

export type FormSchema = z.infer<typeof formSchema>;
