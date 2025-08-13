/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import React from "react";
import ReactDOM from "react-dom";
import { FormConfigProvider } from "@js/oarepo_ui";
import { RequestDetail } from "./components";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Overridable, {
  OverridableContext,
  overrideStore,
} from "react-overridable";
import overrides from "@js/oarepo_requests_common/overrides";

const recordRequestsAppDiv = document.getElementById("request-detail");

const overriddenComponents = {
  ...overrides,
  ...overrideStore.getAll(),
};

const request = recordRequestsAppDiv.dataset?.request
  ? JSON.parse(recordRequestsAppDiv.dataset.request)
  : {};
const formConfig = recordRequestsAppDiv.dataset?.formConfig
  ? JSON.parse(recordRequestsAppDiv.dataset.formConfig)
  : {};
const queryClient = new QueryClient();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <FormConfigProvider value={{ formConfig }}>
      <QueryClientProvider client={queryClient}>
        <Overridable
          id="OarepoRequests.RequestDetail.container"
          request={request}
        >
          <RequestDetail request={request} />
        </Overridable>
      </QueryClientProvider>
    </FormConfigProvider>
  </OverridableContext.Provider>,
  recordRequestsAppDiv
);
