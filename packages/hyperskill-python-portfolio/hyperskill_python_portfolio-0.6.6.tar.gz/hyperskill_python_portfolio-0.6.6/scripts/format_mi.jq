["File", "MI Score", "Rank"],
["-", "-", "-"],

# 1. Convert object to an array of entries: [to_entries]
# 2. Sort that array by the key (the file path): [sort_by(.key)]
# 3. Iterate over the now-sorted array: []
# 4. Format each item into our desired array for the table
(to_entries
    | sort_by(.value.mi)
    | .[]
    | [.key, ((.value.mi * 100 | round) / 100), .value.rank]
)
| @tsv
