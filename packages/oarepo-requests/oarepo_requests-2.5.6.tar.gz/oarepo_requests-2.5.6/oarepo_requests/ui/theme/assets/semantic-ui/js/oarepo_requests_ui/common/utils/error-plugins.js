import { setIn } from "formik";
import { serializeErrors } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { encodeUnicodeBase64 } from "@js/oarepo_ui";

export class BeforeActionError extends Error {}

export const cfValidationErrorPlugin = (e, { formik }) => {
  if (e?.response?.data?.request_payload_errors?.length > 0) {
    let errorsObj = {};
    for (const error of e.response.data.request_payload_errors) {
      errorsObj = setIn(errorsObj, error.field, error.messages.join(" "));
    }
    formik?.setErrors(errorsObj);
    return true;
  }
  return null;
};

export const recordValidationErrorsPlugin = (
  e,
  { modalControl, actionExtraContext, requestOrRequestType }
) => {
  const setErrors =
    typeof actionExtraContext?.setErrors === "function"
      ? actionExtraContext.setErrors
      : null;

  if (e?.response?.data?.errors?.length > 0) {
    const errors = serializeErrors(
      e.response.data.errors,
      i18next.t(
        "The request ({{requestType}}) could not be made due to validation errors. Please fix them and try again:",
        {
          requestType:
            requestOrRequestType?.stateful_name || requestOrRequestType.name,
        }
      )
    );
    e.directSubmitMessage =
      e?.response?.data?.message ?? i18next.t("Request could not be executed.");

    if (setErrors) {
      setErrors(errors);
    }

    modalControl?.closeModal();
    return true;
  }

  return null;
};

export const handleRedirectToEditFormPlugin = (
  e,
  { formik, modalControl, requestOrRequestType, actionExtraContext: { record } }
) => {
  if (e?.response?.data?.errors && record?.links?.edit_html) {
    const errorData = {
      errors: e.response.data.errors,
      errorMessage: i18next.t(
        "The request ({{requestType}}) could not be made due to validation errors. Please fix them and try again:",
        {
          requestType:
            requestOrRequestType?.stateful_name || requestOrRequestType.name,
        }
      ),
    };

    const jsonErrors = JSON.stringify(errorData);
    const base64EncodedErrors = encodeUnicodeBase64(jsonErrors);

    formik?.setFieldError(
      "api",
      i18next.t("Record has validation errors. Redirecting to form...")
    );
    e.directSubmitMessage = i18next.t(
      "Record has validation errors. Redirecting to form..."
    );
    setTimeout(() => {
      window.location.href = record.links.edit_html + `#${base64EncodedErrors}`;
      modalControl?.closeModal();
    }, 2500);

    return true;
  } else if (e?.response?.data?.errors) {
    formik?.setFieldError(
      "api",
      i18next.t(
        "Record has validation errors. Please click the 'Edit metadata' button and then try again."
      )
    );
    e.directSubmitMessage = i18next.t(
      "Record has validation errors. Please click the 'Edit metadata' button and then try again."
    );
    return true;
  }
  return null;
};

export const beforeActionFormErrorPlugin = (e, { modalControl }) => {
  if (e instanceof BeforeActionError) {
    modalControl?.closeModal();
    return true;
  }
  return null;
};

export const defaultErrorHandlingPlugin = (e, { formik }) => {
  if (e?.response?.data?.errors) {
    formik?.setFieldError(
      "api",
      i18next.t(
        "The request could not be created due to validation errors. Please correct the errors and try again."
      )
    );
  } else {
    formik?.setFieldError(
      "api",
      e?.response?.data?.message ??
        i18next.t(
          "The action could not be executed. Please try again in a moment."
        )
    );
  }
};
