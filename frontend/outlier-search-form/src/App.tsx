import { useEffect, useMemo, useRef, useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { formSchema, type FormSchema } from "./schema";
import type { ComponentData, FormValues, StreamlitComponentLike } from "./types";
import {
  AdvancedTray,
  Button,
  FieldLabel,
  NumberInput,
  SectionTitle,
  SegmentedField,
  SelectField,
  Shell,
  TextInput,
  VisibilityCard,
} from "./components/ui";

function normalizeValues(values: FormSchema): FormValues {
  return {
    ...values,
    min_views: Number(values.min_views),
    min_subscribers: Number(values.min_subscribers),
    max_subscribers: Number(values.max_subscribers),
    search_pages: Number(values.search_pages),
    baseline_channels: Number(values.baseline_channels),
    baseline_videos: Number(values.baseline_videos),
    custom_start: values.timeframe === "Custom" ? values.custom_start || "" : "",
    custom_end: values.timeframe === "Custom" ? values.custom_end || "" : "",
  };
}

function toSelectOptions(values: Array<string | number>) {
  return values.map((value) => ({ label: typeof value === "number" ? `${value}` : value, value: String(value) }));
}

export function App({ component }: { component: StreamlitComponentLike }) {
  const data = component.data as ComponentData;
  const [showAdvanced, setShowAdvanced] = useState(false);
  const draftTimeout = useRef<number | null>(null);
  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: data.values,
    mode: "onSubmit",
  });

  const timeframe = form.watch("timeframe");

  useEffect(() => {
    form.reset(data.values);
  }, [data.values, form]);

  useEffect(() => {
    const subscription = form.watch((values) => {
      if (draftTimeout.current) {
        window.clearTimeout(draftTimeout.current);
      }
      draftTimeout.current = window.setTimeout(() => {
        component.setStateValue("draft", normalizeValues(values as FormSchema));
      }, 120);
    });
    return () => {
      subscription.unsubscribe();
      if (draftTimeout.current) {
        window.clearTimeout(draftTimeout.current);
      }
    };
  }, [component, form]);

  const minViewOptions = useMemo(
    () =>
      data.options.minViews.map((value) => ({
        label: value === 0 ? "No Minimum" : `${value.toLocaleString()}+`,
        value: String(value),
      })),
    [data.options.minViews],
  );

  const advancedSearchOptions = useMemo(() => toSelectOptions(data.options.advanced.searchPages), [data.options.advanced.searchPages]);
  const baselineChannelOptions = useMemo(
    () => toSelectOptions(data.options.advanced.baselineChannels),
    [data.options.advanced.baselineChannels],
  );
  const baselineVideoOptions = useMemo(
    () => toSelectOptions(data.options.advanced.baselineVideos),
    [data.options.advanced.baselineVideos],
  );

  const onSubmit = form.handleSubmit((values) => {
    component.setTriggerValue("submitted", normalizeValues(values));
  });

  return (
    <div className="of-font-ui of-mx-auto of-max-w-[1040px] of-text-text">
      {data.prefillNote ? (
        <div className="of-mb-4 of-inline-flex of-items-center of-gap-2 of-rounded-full of-border of-border-accent-soft/20 of-bg-accent/14 of-px-4 of-py-2 of-text-[12px] of-font-medium of-text-[#E6DFFC]">
          Suggested Query Loaded
          <span className="of-text-subtle">{data.prefillNote}</span>
        </div>
      ) : null}

      <Shell>
        <SectionTitle
          title="Search A Niche"
          copy="Scan any topic, tighten the filters, and surface the videos that are outperforming their likely baseline."
        />

        <form
          className="of-space-y-[18px]"
          onSubmit={(event) => {
            event.preventDefault();
            void onSubmit(event);
          }}
        >
          <div className="of-grid of-gap-3 lg:of-grid-cols-12">
            <div className="lg:of-col-span-8">
              <FieldLabel label="Niche Or Keyword" error={form.formState.errors.query?.message} />
              <TextInput
                placeholder="AI Automation, Documentary Storytelling, Science Shorts, Luxury Fitness..."
                {...form.register("query")}
              />
            </div>
            <div className="lg:of-col-span-4">
              <FieldLabel label="Actions" />
              <div className="of-grid of-grid-cols-2 of-gap-3">
                <Button type="submit" variant="primary" disabled={data.disabled.submit}>
                  Find Outliers
                </Button>
                <Button
                  type="button"
                  onClick={() => {
                    form.reset(data.values);
                    component.setTriggerValue("reset", true);
                  }}
                >
                  Reset Filters
                </Button>
              </div>
            </div>
          </div>

          <div className="of-grid of-gap-3 md:of-grid-cols-2 xl:of-grid-cols-4">
            <div>
              <FieldLabel label="Timeframe" />
              <Controller
                control={form.control}
                name="timeframe"
                render={({ field }) => <SelectField value={field.value} onValueChange={field.onChange} options={toSelectOptions(data.options.timeframes)} />}
              />
            </div>
            <div>
              <FieldLabel label="Match Mode" />
              <Controller
                control={form.control}
                name="match_mode"
                render={({ field }) => <SegmentedField value={field.value} onValueChange={field.onChange} options={data.options.matchModes} />}
              />
            </div>
            <div>
              <FieldLabel label="Region" />
              <Controller
                control={form.control}
                name="region"
                render={({ field }) => <SelectField value={field.value} onValueChange={field.onChange} options={toSelectOptions(data.options.regions)} />}
              />
            </div>
            <div>
              <FieldLabel label="Language" />
              <Controller
                control={form.control}
                name="language"
                render={({ field }) => <SelectField value={field.value} onValueChange={field.onChange} options={toSelectOptions(data.options.languages)} />}
              />
            </div>
          </div>

          {timeframe === "Custom" ? (
            <div className="of-grid of-gap-3 md:of-grid-cols-2">
              <div>
                <FieldLabel label="Custom Start Date" error={form.formState.errors.custom_start?.message} />
                <TextInput type="date" {...form.register("custom_start")} />
              </div>
              <div>
                <FieldLabel label="Custom End Date" error={form.formState.errors.custom_end?.message} />
                <TextInput type="date" {...form.register("custom_end")} />
              </div>
            </div>
          ) : null}

          <div className="of-grid of-gap-3 md:of-grid-cols-2 xl:of-grid-cols-4">
            <div>
              <FieldLabel label="Freshness Focus" />
              <Controller
                control={form.control}
                name="freshness_focus"
                render={({ field }) => <SelectField value={field.value} onValueChange={field.onChange} options={toSelectOptions(data.options.freshness)} />}
              />
            </div>
            <div>
              <FieldLabel label="Duration Preference" />
              <Controller
                control={form.control}
                name="duration_preference"
                render={({ field }) => <SelectField value={field.value} onValueChange={field.onChange} options={toSelectOptions(data.options.durations)} />}
              />
            </div>
            <div>
              <FieldLabel label="Language Strictness" />
              <Controller
                control={form.control}
                name="language_strictness"
                render={({ field }) => <SegmentedField value={field.value} onValueChange={field.onChange} options={data.options.strictness} />}
              />
            </div>
            <div>
              <FieldLabel label="Minimum Views" />
              <Controller
                control={form.control}
                name="min_views"
                render={({ field }) => (
                  <SelectField
                    value={String(field.value)}
                    onValueChange={(value) => field.onChange(Number(value))}
                    options={minViewOptions}
                  />
                )}
              />
            </div>
          </div>

          <div className="of-grid of-gap-3 xl:of-grid-cols-12">
            <div className="xl:of-col-span-8">
              <div className="of-mb-2 of-text-[13px] of-font-semibold of-text-text">Channel Size</div>
              <div className="of-grid of-gap-3 md:of-grid-cols-2">
                <div>
                  <FieldLabel label="Minimum Subscribers" />
                  <NumberInput {...form.register("min_subscribers", { valueAsNumber: true })} />
                </div>
                <div>
                  <FieldLabel
                    label="Maximum Subscribers"
                    error={form.formState.errors.max_subscribers?.message}
                    helper="Leave At 0 To Keep The Upper Bound Open."
                  />
                  <NumberInput {...form.register("max_subscribers", { valueAsNumber: true })} />
                </div>
              </div>
            </div>
            <div className="xl:of-col-span-4">
              <FieldLabel label="Visibility Handling" />
              <Controller
                control={form.control}
                name="include_hidden"
                render={({ field }) => (
                  <VisibilityCard checked={Boolean(field.value)} onCheckedChange={field.onChange} />
                )}
              />
            </div>
          </div>

          <div>
            <FieldLabel label="Exclude Keywords" helper="Use commas to exclude obvious false positives from the scan." />
            <TextInput placeholder="News, Reaction, Podcast Clips" {...form.register("exclude_keywords")} />
          </div>

          <AdvancedTray open={showAdvanced} onOpenChange={setShowAdvanced}>
            <div className="of-grid of-gap-3 md:of-grid-cols-3">
              <div>
                <FieldLabel label="Search Depth" helper="Each extra page adds about 100 search quota units." />
                <Controller
                  control={form.control}
                  name="search_pages"
                  render={({ field }) => (
                    <SelectField
                      value={String(field.value)}
                      onValueChange={(value) => field.onChange(Number(value))}
                      options={advancedSearchOptions}
                    />
                  )}
                />
              </div>
              <div>
                <FieldLabel label="Baseline Channels" />
                <Controller
                  control={form.control}
                  name="baseline_channels"
                  render={({ field }) => (
                    <SelectField
                      value={String(field.value)}
                      onValueChange={(value) => field.onChange(Number(value))}
                      options={baselineChannelOptions}
                    />
                  )}
                />
              </div>
              <div>
                <FieldLabel label="Baseline Uploads Per Channel" />
                <Controller
                  control={form.control}
                  name="baseline_videos"
                  render={({ field }) => (
                    <SelectField
                      value={String(field.value)}
                      onValueChange={(value) => field.onChange(Number(value))}
                      options={baselineVideoOptions}
                    />
                  )}
                />
              </div>
            </div>
          </AdvancedTray>

          <div className="of-text-[12px] of-leading-6 of-text-subtle">
            Use tighter filters when you want a cleaner research set, and broader settings when you want a wider scouting pass.
          </div>
        </form>
      </Shell>
    </div>
  );
}
