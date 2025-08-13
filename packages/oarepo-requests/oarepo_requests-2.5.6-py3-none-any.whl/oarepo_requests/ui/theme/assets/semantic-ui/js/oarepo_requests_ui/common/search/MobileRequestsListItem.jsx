// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/oarepo_dashboard";
import React from "react";
import { RequestTypeLabel } from "./labels/TypeLabels";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { default as RequestTypeIcon } from "@js/invenio_requests/components/RequestTypeIcon";
import { Item } from "semantic-ui-react";
import PropTypes from "prop-types";
import { ResultItemMeta } from "./ResultItemMeta";

export const MobileRequestsListItem = ({ result, detailsURL }) => {
  return (
    <Item
      key={result.id}
      className="mobile only rel-p-1 rel-mb-1 result-list-item request"
    >
      <Item.Content className="centered">
        <Item.Extra>
          {result.type && (
            <RequestTypeLabel requestName={result.name || result.type} />
          )}
          {result.status && <RequestStatusLabel status={result.status_code} />}
        </Item.Extra>
        {result?.topic?.status === "removed" ? (
          <Item.Header className="truncate-lines-2 rel-mt-1">
            <RequestTypeIcon type={result.type} />
            {result?.name || result?.title}
            {result?.topic?.label && (
              <span className="ml-5">({result?.topic?.label})</span>
            )}
          </Item.Header>
        ) : (
          <Item.Header className="truncate-lines-2 rel-mt-1">
            <a className="header-link p-0" href={detailsURL}>
              <RequestTypeIcon type={result.type} />
              {result?.name || result?.title}
              {result?.topic?.label && (
                <span className="ml-5">({result?.topic?.label})</span>
              )}
            </a>
          </Item.Header>
        )}
        <p className="rel-mt-1">
          {result.description || i18next.t("No description")}
        </p>
        <ResultItemMeta result={result} />
      </Item.Content>
    </Item>
  );
};

MobileRequestsListItem.propTypes = {
  result: PropTypes.object.isRequired,
  detailsURL: PropTypes.string.isRequired,
};
