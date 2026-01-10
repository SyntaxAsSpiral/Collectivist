# Collectivist CLI Viewer - Nushell Interactive Dashboard
# Run with: nu .collection/view.nu

# Load collection data
let collection_dir = ($env.PWD | path join ".collection")
let index_file = ($collection_dir | path join "index.yaml")

if not ($index_file | path exists) {
    print "❌ No collection data found. Run 'python -m .collection update' first."
    exit 1
}

# Load and parse YAML data
let data = (open $index_file)

# Display collection header
print $"🤖 Collectivist Dashboard"
print $"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print $"Collection: ($data.collection_id)"
print $"Domain: ($data.domain)"
print $"Items: ($data.total_items)"
print $"Last scan: ($data.last_scan)"
print $"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print ""

# Show status summary
print "📊 Status Summary:"
let status_summary = ($data.items | group-by {|item| $item.status.git_status or "unknown"} | transpose status count)
$status_summary | each {|row|
    let status = $row.status
    let count = ($row.count | length)
    let emoji = match $status {
        "up_to_date" => "✅"
        "updates_available" => "🔄"
        "modified" => "✏️"
        "ahead_of_remote" => "⬆️"
        "no_remote" => "🚫"
        "error" => "❌"
        _ => "❓"
    }
    print $"  ($emoji) ($status | str replace '_' ' ' | str title): ($count)"
}
print ""

# Show category summary
print "📂 Category Summary:"
let category_summary = ($data.items | group-by {|item| $item.category or "uncategorized"} | transpose category count)
$category_summary | each {|row|
    let category = $row.category
    let count = ($row.count | length)
    print $"  📁 ($category | str replace '_' ' ' | str title): ($count)"
}
print ""

# Interactive menu
print "🎛️  Choose an action:"
print "  1. View all items"
print "  2. Browse by category"
print "  3. Search items"
print "  4. Show recent items"
print "  5. Exit"
print ""

mut choice = ""
while $choice != "5" {
    $choice = (input "Enter choice (1-5): ")

    match $choice {
        "1" => {
            print "\n📋 All Items:"
            print "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            $data.items | select name category status.git_status description | table -e
            print ""
        }
        "2" => {
            print "\n📂 Available categories:"
            let categories = ($data.items.category | uniq | where {|c| $c != null})
            $categories | enumerate | each {|item|
                print $"  ($item.index + 1). ($item.item | str replace '_' ' ' | str title)"
            }
            print ""

            let cat_choice = (input "Enter category number: ")
            try {
                let cat_index = (($cat_choice | into int) - 1)
                let selected_cat = ($categories | get $cat_index)

                print $"\n📂 Items in category: ($selected_cat | str replace '_' ' ' | str title)"
                print "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                $data.items | where {|item| $item.category == $selected_cat} | select name status.git_status description | table -e
                print ""
            } catch {
                print "❌ Invalid category number"
                print ""
            }
        }
        "3" => {
            let query = (input "\n🔍 Enter search term: ")
            print $"\n🔍 Search results for '($query)':"
            print "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

            let results = ($data.items | where {|item|
                ($item.name or "" | str downcase | str contains ($query | str downcase)) or
                ($item.description or "" | str downcase | str contains ($query | str downcase)) or
                ($item.category or "" | str downcase | str contains ($query | str downcase))
            })

            if ($results | length) > 0 {
                $results | select name category status.git_status description | table -e
            } else {
                print "No items found matching your search."
            }
            print ""
        }
        "4" => {
            print "\n🕒 Recent items (last 10):"
            print "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            $data.items | sort-by {|item|
                try {
                    $item.metadata.modified or $item.metadata.created or "1970-01-01"
                } catch {
                    "1970-01-01"
                }
            } | reverse | first 10 | select name category status.git_status description | table -e
            print ""
        }
        "5" => {
            print "👋 Goodbye!"
        }
        _ => {
            print "❌ Invalid choice. Please enter 1-5."
            print ""
        }
    }
}