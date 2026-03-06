---
name: fix-migrations
description: Automatically resolve Django migration conflicts after merging or rebasing
argument-hint: [dry-run]
---

Automatically resolve Django migration conflicts in PostHog by renumbering conflicting migrations.

**What it does:**
- Detects migrations added in your branch that conflict with master
- Renumbers them sequentially after the latest migration in master
- Updates dependency chains within the migrations
- Updates `max_migration.txt` with the new last migration

**Arguments:**
- `dry-run` - Preview changes without applying them (optional)
- (no argument) - Apply changes automatically

**Usage examples:**
- `/fix-migrations` - Fix migration conflicts automatically
- `/fix-migrations dry-run` - Preview what changes would be made

## Instructions

Run the migration fixer script to detect and resolve conflicts:

```bash
#!/bin/bash
set -e

# Get the argument (if any)
ARG="${ARGUMENTS:-}"
DRY_RUN=false
if [ "$ARG" = "dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
    echo ""
fi

# Change to PostHog directory
cd /Users/arthur/Code/posthog

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Get the main/master branch name
MAIN_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "master")
if ! git show-ref --verify --quiet refs/remotes/origin/$MAIN_BRANCH; then
    MAIN_BRANCH="main"
fi

echo "📋 Checking for migration conflicts with $MAIN_BRANCH branch..."
echo ""

# Get migrations added in current branch
BRANCH_MIGRATIONS=$(git diff --name-only $MAIN_BRANCH...HEAD -- 'posthog/migrations/*.py' | grep -v __pycache__ | sort || true)

if [ -z "$BRANCH_MIGRATIONS" ]; then
    echo "✅ No new migrations found in current branch"
    exit 0
fi

echo "📌 Migrations in current branch:"
for migration in $BRANCH_MIGRATIONS; do
    basename "$migration"
done
echo ""

# Get the latest migration number from master
MASTER_MAX_MIGRATION=$(git show $MAIN_BRANCH:posthog/migrations/max_migration.txt 2>/dev/null | head -1 || echo "")
if [ -z "$MASTER_MAX_MIGRATION" ]; then
    echo "❌ Error: Could not determine latest migration from $MAIN_BRANCH"
    exit 1
fi

# Extract the number from the migration name (e.g., "0984_clear_tokens" -> "984")
MASTER_MAX_NUMBER=$(echo "$MASTER_MAX_MIGRATION" | grep -oE '^[0-9]+' || echo "0")

echo "📍 Latest migration in $MAIN_BRANCH: $MASTER_MAX_MIGRATION (number: $MASTER_MAX_NUMBER)"
echo ""

# Check for existing migrations with the same or higher numbers
CONFLICTS=()
for migration_path in $BRANCH_MIGRATIONS; do
    migration_file=$(basename "$migration_path")
    migration_number=$(echo "$migration_file" | grep -oE '^[0-9]+' || echo "0")

    # Check if this migration already exists in master
    if git ls-tree $MAIN_BRANCH -- "posthog/migrations/$migration_file" > /dev/null 2>&1; then
        echo "✅ Migration $migration_file already in $MAIN_BRANCH (no conflict)"
        continue
    fi

    # Check if there's a conflict (same or overlapping number)
    existing_with_number=$(ls posthog/migrations/${migration_number}_*.py 2>/dev/null | grep -v "$migration_file" || true)
    if [ -n "$existing_with_number" ] || [ "$migration_number" -le "$MASTER_MAX_NUMBER" ]; then
        CONFLICTS+=("$migration_path")
    fi
done

if [ ${#CONFLICTS[@]} -eq 0 ]; then
    echo "✅ No migration conflicts found"
    exit 0
fi

echo "⚠️  Found ${#CONFLICTS[@]} conflicting migration(s) to fix:"
for conflict in "${CONFLICTS[@]}"; do
    basename "$conflict"
done
echo ""

# Sort conflicts by their current numbers
IFS=$'\n' SORTED_CONFLICTS=($(printf '%s\n' "${CONFLICTS[@]}" | sort))

# Calculate new migration numbers
NEXT_NUMBER=$((MASTER_MAX_NUMBER + 1))
RENAMES=()
DEPENDENCY_UPDATES=()

echo "📝 Planning changes:"
echo ""

for conflict_path in "${SORTED_CONFLICTS[@]}"; do
    old_name=$(basename "$conflict_path")
    old_number=$(echo "$old_name" | grep -oE '^[0-9]+')
    old_suffix=$(echo "$old_name" | sed "s/^${old_number}_//")

    # Format with leading zeros
    new_number=$(printf "%04d" $NEXT_NUMBER)
    new_name="${new_number}_${old_suffix}"

    echo "  • $old_name → $new_name"
    RENAMES+=("$conflict_path:posthog/migrations/$new_name")

    # Track dependency updates needed
    DEPENDENCY_UPDATES+=("${old_number}_:${new_number}_")

    NEXT_NUMBER=$((NEXT_NUMBER + 1))
done

# Determine the new last migration for max_migration.txt
LAST_MIGRATION_NAME=$(basename "${RENAMES[-1]}" | cut -d: -f2 | xargs basename | sed 's/\.py$//')

echo ""
echo "📄 Will update max_migration.txt to: $LAST_MIGRATION_NAME"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "✨ Dry run complete - no changes made"
    exit 0
fi

echo "🔄 Applying changes..."
echo ""

# Perform the renames
for rename in "${RENAMES[@]}"; do
    old_path=$(echo "$rename" | cut -d: -f1)
    new_path=$(echo "$rename" | cut -d: -f2)

    if [ -f "$old_path" ]; then
        mv "$old_path" "$new_path"
        echo "  ✓ Renamed $(basename "$old_path") → $(basename "$new_path")"
    fi
done

echo ""
echo "🔗 Updating migration dependencies..."

# Update dependencies in all renamed files
for rename in "${RENAMES[@]}"; do
    new_path=$(echo "$rename" | cut -d: -f2)

    # Update dependencies to point to renamed migrations
    for dep_update in "${DEPENDENCY_UPDATES[@]}"; do
        old_prefix=$(echo "$dep_update" | cut -d: -f1)
        new_prefix=$(echo "$dep_update" | cut -d: -f2)

        # Use sed to update the dependency
        sed -i '' "s/\"${old_prefix}/\"${new_prefix}/g" "$new_path" 2>/dev/null || \
        sed -i "s/\"${old_prefix}/\"${new_prefix}/g" "$new_path"
    done
done

# Update dependencies to point to the last master migration for the first renamed migration
if [ ${#RENAMES[@]} -gt 0 ]; then
    first_new_path=$(echo "${RENAMES[0]}" | cut -d: -f2)

    # Find the current dependency and replace it with the master max migration
    sed -i '' "s/(\"posthog\", \"[0-9]*_[^\"]*\")/(\"posthog\", \"$MASTER_MAX_MIGRATION\")/g" "$first_new_path" 2>/dev/null || \
    sed -i "s/(\"posthog\", \"[0-9]*_[^\"]*\")/(\"posthog\", \"$MASTER_MAX_MIGRATION\")/g" "$first_new_path"

    echo "  ✓ Updated first migration to depend on $MASTER_MAX_MIGRATION"
fi

# Update subsequent migrations to depend on each other
for i in "${!RENAMES[@]}"; do
    if [ $i -gt 0 ]; then
        current_path=$(echo "${RENAMES[$i]}" | cut -d: -f2)
        prev_name=$(basename "${RENAMES[$((i-1))]}" | cut -d: -f2 | sed 's/\.py$//')

        # Update to depend on previous migration
        sed -i '' "s/(\"posthog\", \"[0-9]*_[^\"]*\")/(\"posthog\", \"$prev_name\")/g" "$current_path" 2>/dev/null || \
        sed -i "s/(\"posthog\", \"[0-9]*_[^\"]*\")/(\"posthog\", \"$prev_name\")/g" "$current_path"

        echo "  ✓ Updated $(basename "$current_path") to depend on $prev_name"
    fi
done

echo ""
echo "📄 Updating max_migration.txt..."

# Update max_migration.txt
echo "$LAST_MIGRATION_NAME" > posthog/migrations/max_migration.txt
echo "  ✓ Updated to $LAST_MIGRATION_NAME"

echo ""
echo "✅ Migration conflicts resolved successfully!"
echo ""
echo "📋 Summary:"
echo "  • Renamed ${#RENAMES[@]} migration file(s)"
echo "  • Updated dependency chains"
echo "  • Updated max_migration.txt to $LAST_MIGRATION_NAME"
echo ""
echo "💡 Next steps:"
echo "  1. Review the changes with: git status"
echo "  2. Test migrations with: python manage.py migrate"
echo "  3. Commit the changes when ready"
```

## After completion

Assess how this skill performed:
- If the user had to provide significant guidance, corrections, or workarounds to get the task done, recommend running `/improve-skill` to capture those learnings. Explain briefly what could be improved.
- If the skill ran smoothly with minimal intervention, offer it as an option: "Would you like to run `/improve-skill` to refine this skill based on this session?"
