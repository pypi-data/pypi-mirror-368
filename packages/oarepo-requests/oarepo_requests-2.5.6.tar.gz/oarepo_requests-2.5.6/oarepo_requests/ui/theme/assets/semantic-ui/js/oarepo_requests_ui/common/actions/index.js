/*
 * Copyright (C) 2024 CESNET z.s.p.o.
 *
 * oarepo-requests is free software; you can redistribute it and/or
 * modify it under the terms of the MIT License; see LICENSE file for more
 * details.
 */
import { REQUEST_TYPE } from "@js/oarepo_requests_common";
import Accept from "./Accept";
import Decline from "./Decline";
import Cancel from "./Cancel";
import Create from "./Create";
import Submit from "./Submit";
import ModalCreateAndSubmit from "./ModalCreateAndSubmit";
import DirectCreateAndSubmit from "./DirectCreateAndSubmit";

export const mapLinksToActions = (
  requestOrRequestType,
  customFields,
  extraData
) => {
  const hasLongForm = extraData?.editable;
  const actionComponents = [];
  for (const actionKey of Object.keys(requestOrRequestType.links?.actions)) {
    switch (actionKey) {
      case REQUEST_TYPE.ACCEPT:
        actionComponents.push({
          name: REQUEST_TYPE.ACCEPT,
          component: Accept,
        });
        actionComponents.push({
          name: REQUEST_TYPE.DECLINE,
          component: Decline,
        });
        break;
      case REQUEST_TYPE.CANCEL:
        actionComponents.push({
          name: REQUEST_TYPE.CANCEL,
          component: Cancel,
        });
        break;
      case REQUEST_TYPE.CREATE:
        // requestOrRequestType is requestType here
        if (customFields?.ui && hasLongForm) {
          actionComponents.push({
            name: REQUEST_TYPE.SAVE,
            component: Create,
          });
        }
        actionComponents.push({
          name: REQUEST_TYPE.SUBMIT,
          component: ModalCreateAndSubmit,
        });
        break;
      case REQUEST_TYPE.SUBMIT:
        actionComponents.push({
          name: REQUEST_TYPE.SUBMIT,
          component: Submit,
        });
        if (customFields?.ui) {
          actionComponents.push({
            name: REQUEST_TYPE.SAVE,
            component: Create,
          });
        }
        break;
      default:
        break;
    }
  }
  return actionComponents;
};

export { DirectCreateAndSubmit };
