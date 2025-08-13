import React, { useRef, useEffect } from "react";
import { Grid, Loader, Segment } from "semantic-ui-react";
import PropTypes from "prop-types";

export const TopicPreview = ({ request }) => {
  const iframeRef = useRef(null);
  const [pxHeight, setPxHeight] = React.useState(0);
  const [loading, setLoading] = React.useState(true);

  const updateIframeHeight = () => {
    setPxHeight(iframeRef.current.contentWindow.document.body.scrollHeight);
  };

  useEffect(() => {
    const iframe = iframeRef.current;
    if (iframe) {
      iframe.contentWindow.addEventListener("resize", updateIframeHeight);
    }
    return () => {
      iframe.contentWindow.removeEventListener("resize", updateIframeHeight);
    };
  }, []);

  return (
    <Grid.Row>
      <Grid.Column>
        {loading && (
          <Segment placeholder loading className="borderless">
            <Loader active size="massive" />
          </Segment>
        )}
        <iframe
          ref={iframeRef}
          src={request.links.topic.self_html + "?embed=true"}
          onLoad={() => {
            updateIframeHeight();
            setLoading(false);
          }}
          title={request.topic.label + " record preview"}
          width="100%"
          height={pxHeight + "px"}
          style={{
            outline: "none",
            border: "none",
            overflow: "hidden",
            margin: 0,
          }}
        />
      </Grid.Column>
    </Grid.Row>
  );
};

TopicPreview.propTypes = {
  request: PropTypes.object,
};
