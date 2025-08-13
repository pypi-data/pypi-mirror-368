import React, { useState } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Message, Feed, Dimmer, Loader, Pagination } from "semantic-ui-react";
import { CommentSubmitForm, TimelineEvent } from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { httpApplicationJson } from "@js/oarepo_ui";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export const Timeline = ({ request, timelinePageSize }) => {
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const { data, error, isLoading, refetch } = useQuery(
    ["requestEvents", request.id, page],
    () =>
      // q=!(type:T) to eliminate system created events
      httpApplicationJson.get(
        `${request.links?.timeline}?q=!(type:T)&page=${page}&size=${timelinePageSize}&sort=newest&expand=1`
      ),
    {
      enabled: !!request.links?.timeline,
      // when you click on rich editor and then back to the window, it considers
      // that this is focus on the window itself, so unable to use refetchOnWindowFocus
      refetchOnWindowFocus: false,
      refetchInterval: 10000,
    }
  );

  const commentSubmitMutation = useMutation(
    (values) =>
      httpApplicationJson.post(request.links?.comments + "?expand=1", values),
    {
      onSuccess: (response) => {
        if (response.status === 201) {
          queryClient.setQueryData(
            ["requestEvents", request.id, page],
            (oldData) => {
              if (!oldData) return;
              // a bit ugly, but it is a limitation of react query when data you recieve is nested
              const newHits = [...oldData.data.hits.hits];
              if (oldData.data.hits.total + 1 > timelinePageSize) {
                newHits.pop();
              }
              return {
                ...oldData,
                data: {
                  ...oldData.data,
                  hits: {
                    ...oldData.data.hits,
                    total: oldData.data.hits.total + 1,
                    hits: [response.data, ...newHits],
                  },
                },
              };
            }
          );
        }
        setTimeout(() => refetch(), 1000);
      },
    }
  );

  const handlePageChange = (activePage) => {
    if (activePage === page) return;
    setPage(activePage);
  };
  const events = data?.data?.hits?.hits;
  const totalPages = Math.ceil(data?.data?.hits?.total / timelinePageSize);
  return (
    <Dimmer.Dimmable blurring dimmed={isLoading}>
      <Dimmer active={isLoading} inverted>
        <Loader indeterminate size="big">
          {i18next.t("Loading timeline...")}
        </Loader>
      </Dimmer>
      <div className="rel-mb-5">
        <CommentSubmitForm commentSubmitMutation={commentSubmitMutation} />
      </div>
      {error && (
        <Message negative>
          <Message.Header>
            {i18next.t("Error while fetching timeline events")}
          </Message.Header>
        </Message>
      )}
      {events?.length > 0 && (
        <Feed>
          {events.map((event) => (
            <TimelineEvent
              key={event.id}
              event={event}
              // necessary for query invalidation and setting state of the request events query
              requestId={request.id}
              page={page}
            />
          ))}
        </Feed>
      )}
      {data?.data?.hits?.total > timelinePageSize && (
        <div className="centered rel-mb-1">
          <Pagination
            size="mini"
            activePage={page}
            totalPages={totalPages}
            onPageChange={(_, { activePage }) => handlePageChange(activePage)}
            ellipsisItem={null}
            firstItem={null}
            lastItem={null}
          />
        </div>
      )}
    </Dimmer.Dimmable>
  );
};

Timeline.propTypes = {
  request: PropTypes.object,
  timelinePageSize: PropTypes.number,
};

Timeline.defaultProps = {
  timelinePageSize: 25,
};
