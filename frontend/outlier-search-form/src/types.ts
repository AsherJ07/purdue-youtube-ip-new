export type FormValues = {
  query: string;
  timeframe: string;
  custom_start: string;
  custom_end: string;
  match_mode: string;
  region: string;
  language: string;
  freshness_focus: string;
  duration_preference: string;
  language_strictness: string;
  min_views: number;
  min_subscribers: number;
  max_subscribers: number;
  include_hidden: boolean;
  exclude_keywords: string;
  search_pages: number;
  baseline_channels: number;
  baseline_videos: number;
};

export type FormOptions = {
  timeframes: string[];
  matchModes: string[];
  regions: string[];
  languages: string[];
  freshness: string[];
  durations: string[];
  strictness: string[];
  minViews: number[];
  advanced: {
    searchPages: number[];
    baselineChannels: number[];
    baselineVideos: number[];
  };
};

export type ComponentData = {
  values: FormValues;
  options: FormOptions;
  disabled: {
    submit: boolean;
  };
  prefillNote: string;
};

export type StreamlitComponentLike = {
  data: ComponentData;
  parentElement: HTMLElement;
  setStateValue: (name: string, value: unknown) => void;
  setTriggerValue: (name: string, value: unknown) => void;
};
