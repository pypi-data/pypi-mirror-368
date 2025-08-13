// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/oarepo_dashboard";
import { default as RequestTypeIcon } from "@js/invenio_requests/components/RequestTypeIcon";
import React from "react";
import { RequestTypeLabel } from "./labels/TypeLabels";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { Item } from "semantic-ui-react";
import PropTypes from "prop-types";
import { ResultItemMeta } from "./ResultItemMeta";

export const ComputerTabletRequestsListItem = ({ result, detailsURL }) => {
  return (
    <Item
      key={result.id}
      className="computer tablet only rel-p-1 rel-mb-1 result-list-item request"
    >
      <div className="status-icon mr-10">
        <Item.Content verticalAlign="top">
          <Item.Extra>
            <RequestTypeIcon type={result.type} />
          </Item.Extra>
        </Item.Content>
      </div>
      <Item.Content>
        <Item.Extra>
          {result.type && (
            <RequestTypeLabel requestName={result.name || result.type} />
          )}
          {result.status && <RequestStatusLabel status={result.status_code} />}
        </Item.Extra>
        {result?.topic?.status === "removed" ? (
          <Item.Header className="mt-5">
            {result?.title || result?.name}
            {result?.topic?.label && (
              <span className="ml-5">({result?.topic?.label})</span>
            )}
          </Item.Header>
        ) : (
          <Item.Header className="truncate-lines-2  mt-10">
            <a className="header-link" href={detailsURL}>
              {result?.title || result?.name}
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

ComputerTabletRequestsListItem.propTypes = {
  result: PropTypes.object.isRequired,
  detailsURL: PropTypes.string.isRequired,
};
