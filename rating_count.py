from mrjob.job import MRJob
import json

class MRRatingsCount(MRJob):
    """
    Counts how many reviews fall into each rating value (1–5).
    Input: JSON Lines (one JSON object per line).
    Output: (rating, count)
    """

    def mapper(self, _, line):
        # Each line is one JSON review object
        try:
            review = json.loads(line)
        except json.JSONDecodeError:
            # Skip broken lines instead of crashing the whole job
            return

        # The rating is typically stored under the key "overall"
        rating = review.get("overall", None)
        if rating is None:
            return

        # Convert to string to keep keys consistent (e.g., 5.0 vs 5)
        yield str(rating), 1

    def reducer(self, rating, counts):
        # Sum all the 1's for this rating
        yield rating, sum(counts)


if __name__ == "__main__":
    MRRatingsCount.run()