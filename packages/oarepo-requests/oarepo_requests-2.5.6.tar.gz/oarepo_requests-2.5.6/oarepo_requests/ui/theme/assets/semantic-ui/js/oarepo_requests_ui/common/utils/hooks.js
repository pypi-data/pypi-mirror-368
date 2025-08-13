/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import { useMutation } from "@tanstack/react-query";
import { useCallbackContext } from "@js/oarepo_requests_common";
import {
  cfValidationErrorPlugin,
  recordValidationErrorsPlugin,
  defaultErrorHandlingPlugin,
  BeforeActionError,
} from "./error-plugins";

export const useAction = ({
  action,
  requestOrRequestType,
  formik,
  modalControl,
  requestActionName,
} = {}) => {
  const {
    onBeforeAction,
    onAfterAction,
    onErrorPlugins = [],
    actionExtraContext,
    setActionsLocked,
  } = useCallbackContext();

  const handleActionError = (e, variables) => {
    const context = {
      e,
      variables,
      formik,
      modalControl,
      requestOrRequestType,
      requestActionName,
      actionExtraContext,
    };

    for (const plugin of [
      ...onErrorPlugins,
      cfValidationErrorPlugin,
      recordValidationErrorsPlugin,
    ]) {
      const handled = plugin(e, context);
      if (handled) {
        return;
      }
    }

    defaultErrorHandlingPlugin(e, context);
    // if you get an error and you stay on the same page, the actions should
    // be unlocked again, so the user can try again
    setActionsLocked(false);
  };

  return useMutation(
    async (values) => {
      if (onBeforeAction) {
        const shouldProceed = await onBeforeAction({
          formik,
          modalControl,
          requestOrRequestType,
          requestActionName,
          actionExtraContext,
        });
        if (!shouldProceed) {
          throw new BeforeActionError("Could not proceed with the action.");
        }
      }
      const formValues = { ...formik?.values };
      if (values) {
        formValues.payload.content = values;
      }
      return action(requestOrRequestType, formValues);
    },
    {
      onError: handleActionError,
      onSuccess: (data, variables) => {
        if (onAfterAction) {
          onAfterAction({
            data,
            variables,
            formik,
            modalControl,
            requestOrRequestType,
            requestActionName,
            actionExtraContext,
          });
        }
        const redirectionURL =
          data?.data?.links?.ui_redirect_url ||
          data?.data?.links?.topic?.self_html;

        modalControl?.closeModal();

        if (redirectionURL) {
          window.location.href = redirectionURL;
        } else {
          window.location.reload();
        }
      },
    }
  );
};
