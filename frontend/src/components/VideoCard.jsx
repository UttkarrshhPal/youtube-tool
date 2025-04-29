function VideoCard({ video, keyword }) {
  const formatViews = (count) => {
    if (count >= 1000000) {
      return (count / 1000000).toFixed(1) + "M";
    } else if (count >= 1000) {
      return (count / 1000).toFixed(1) + "K";
    }
    return count;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const highlightText = (text, keyword) => {
    if (!text) return "";

    const parts = text.split(new RegExp(`(${keyword})`, "gi"));
    return parts.map((part, index) =>
      part.toLowerCase() === keyword.toLowerCase() ? (
        <span key={index} className="bg-yellow-200 font-medium">
          {part}
        </span>
      ) : (
        part
      )
    );
  };

  const getMatchLabel = (matchTypes) => {
    if (matchTypes.length === 0) return "";

    return matchTypes
      .map((type) => {
        switch (type) {
          case "title":
            return "Title";
          case "description":
            return "Description";
          case "transcript":
            return "Transcript";
          default:
            return type;
        }
      })
      .join(", ");
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden h-full flex flex-col">
      <a
        href={`https://www.youtube.com/watch?v=${video.id}`}
        target="_blank"
        rel="noopener noreferrer"
        className="block relative"
      >
        <img
          src={video.thumbnail}
          alt={video.title}
          className="w-full object-cover h-48"
        />
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
          {formatViews(video.view_count)} views
        </div>
      </a>

      <div className="p-4 flex-grow flex flex-col">
        <h3 className="font-bold text-lg mb-1 line-clamp-2">
          <a
            href={`https://www.youtube.com/watch?v=${video.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-blue-600"
          >
            {highlightText(video.title, keyword)}
          </a>
        </h3>

        <p className="text-gray-600 text-sm mb-2">
          {video.channel_title} • {formatDate(video.published_at)}
        </p>

        {video.match_type.length > 0 && (
          <div className="mb-3">
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              Found in: {getMatchLabel(video.match_type)}
            </span>
          </div>
        )}

        <div className="text-sm text-gray-700 line-clamp-3 mb-3">
          {highlightText(video.description, keyword)}
        </div>

        {video.transcript_matches.length > 0 && (
          <div className="mt-auto">
            <h4 className="font-medium text-sm mb-2">Transcript Mentions:</h4>
            <div className="bg-gray-50 p-2 rounded-md text-xs max-h-32 overflow-y-auto">
              {video.transcript_matches.map((mention, index) => (
                <p key={index} className="mb-1 last:mb-0">
                  {highlightText(mention, keyword)}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoCard;
