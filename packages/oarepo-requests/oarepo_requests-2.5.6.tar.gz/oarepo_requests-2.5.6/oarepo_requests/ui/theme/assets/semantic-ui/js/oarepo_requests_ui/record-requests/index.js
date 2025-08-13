/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import React from "react";
import ReactDOM from "react-dom";
import { RecordRequests } from "./components";
import {
  handleRedirectToEditFormPlugin,
  cfValidationErrorPlugin,
} from "@js/oarepo_requests_common";

const recordRequestsAppDiv = document.getElementById("record-requests");

if (recordRequestsAppDiv) {
  const record = JSON.parse(recordRequestsAppDiv.dataset.record);
  ReactDOM.render(
    <RecordRequests
      record={record}
      onErrorPlugins={[cfValidationErrorPlugin, handleRedirectToEditFormPlugin]}
      actionExtraContext={{ record }}
    />,
    recordRequestsAppDiv
  );
}
