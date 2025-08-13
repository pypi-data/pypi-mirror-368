/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import _isEmpty from "lodash/isEmpty";
import { httpVnd } from "@js/oarepo_ui";
import _set from "lodash/set";
import _has from "lodash/has";
import _isArray from "lodash/isArray";
import _isObjectLike from "lodash/isObject";
import _every from "lodash/every";
import _isString from "lodash/isString";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import * as Yup from "yup";

export const hasAll = (obj, ...keys) => keys.every((key) => _has(obj, key));

export const hasAny = (obj, ...keys) => keys.some((key) => _has(obj, key));

export const CommentPayloadSchema = Yup.object().shape({
  payload: Yup.object().shape({
    content: Yup.string()
      .min(1, i18next.t("Comment must be at least 1 character long."))
      .required(i18next.t("Comment must be at least 1 character long.")),
    format: Yup.string().equals(["html"], i18next.t("Invalid format.")),
  }),
});

export const getRequestStatusIcon = (requestStatus) => {
  switch (requestStatus?.toLowerCase()) {
    case "created":
      return { name: "clock outline", color: "grey" };
    case "submitted":
      return { name: "clock", color: "grey" };
    case "cancelled":
      return { name: "ban", color: "black" };
    case "accepted":
      return { name: "check circle", color: "green" };
    case "declined":
      return { name: "close", color: "red" };
    case "expired":
      return { name: "hourglass end", color: "orange" };
    case "deleted":
      return { name: "trash", color: "black" };
    case "comment_deleted":
      return { name: "eraser", color: "grey" };
    case "edited":
      return { name: "pencil", color: "grey" };
    default:
      return null;
  }
};

export const getFeedMessage = (eventStatus) => {
  switch (eventStatus?.toLowerCase()) {
    case "created":
      return i18next.t("requestCreated");
    case "submitted":
      return i18next.t("requestSubmitted");
    case "cancelled":
      return i18next.t("requestCancelled");
    case "accepted":
      return i18next.t("requestAccepted");
    case "declined":
      return i18next.t("requestDeclined");
    case "expired":
      return i18next.t("Request expired.");
    case "deleted":
      return i18next.t("requestDeleted");
    case "comment_deleted":
      return i18next.t("deleted comment");
    case "edited":
      return i18next.t("requestEdited");
    default:
      return i18next.t("requestCommented");
  }
};

export const serializeCustomFields = (formData) => {
  if (!formData) return {};
  if (
    _isEmpty(formData.payload) ||
    Object.values(formData.payload).every((value) => !value)
  ) {
    return {};
  } else {
    for (let customField of Object.keys(formData.payload)) {
      if (!formData.payload[customField]) {
        delete formData.payload[customField];
      }
    }
    if (_isEmpty(formData.payload)) {
      return {};
    } else {
      return { payload: formData.payload };
    }
  }
};

export const saveAndSubmit = async (request, formValues) => {
  const response = await createOrSave(request, formValues);
  const submittedRequest = await httpVnd.post(
    response?.data?.links?.actions?.submit,
    {}
  );
  return submittedRequest;
};

export const createOrSave = async (requestOrRequestType, formValues) => {
  const customFieldsData = serializeCustomFields(formValues);
  if (requestOrRequestType?.links?.actions?.create) {
    return await httpVnd.post(
      requestOrRequestType.links.actions.create,
      customFieldsData
    );
  } else {
    return await httpVnd.put(
      requestOrRequestType?.links?.self,
      customFieldsData
    );
  }
};

export const accept = async (request, formData) => {
  return await httpVnd.post(
    request.links?.actions?.accept,
    serializeDataForInvenioApi(formData)
  );
};

export const decline = async (request, formData) => {
  return await httpVnd.post(
    request.links?.actions?.decline,
    serializeDataForInvenioApi(formData)
  );
};

export const cancel = async (request, formData) => {
  return await httpVnd.post(
    request.links?.actions?.cancel,
    serializeDataForInvenioApi(formData)
  );
};

// this is not nice, but unfortunately, as our API vs invenio API are not consistent, I don't see a better way (Invenio api accepts only payload.content and nothing else)
const serializeDataForInvenioApi = (formData) => {
  const serializedData = {};
  if (formData.payload?.content) {
    _set(serializedData, "payload.content", formData.payload.content);
  }
  return serializedData;
};

// Format complex object values for string-like format
export const formatValueToStringLikeFormat = (value) => {
  if (value === null || value === undefined) return "—";
  if (_isArray(value) && _every(value, _isString)) return value.join(", ");
  if (_isObjectLike(value))
    return JSON.stringify(value, null, 2);
  return String(value);
};

// Convert (nested) record field path to human readable format
export const formatNestedRecordFieldPath = (path) => {
  return path
    .replace(/^\//, "")
    .replace(/\/(\d+)\//g, (match, arrayIndex) => {
      return ` › ${parseInt(arrayIndex) + 1} › `;
    })
    .replace(/\/(\d+)$/, (match, arrayIndex) => {
      return ` › ${parseInt(arrayIndex) + 1}`;
    })
    .replace(/\//g, " › ");
};
