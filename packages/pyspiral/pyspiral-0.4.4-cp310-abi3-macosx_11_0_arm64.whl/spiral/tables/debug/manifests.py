from spiral import datetime_
from spiral.core.table import TableScan
from spiral.core.table.manifests import FragmentManifest
from spiral.tables.debug.metrics import _format_bytes


def display_manifests(scan: TableScan):
    """Display all manifests in a scan."""
    if len(scan.table_ids()) != 1:
        raise NotImplementedError("Multiple table scans are not supported.")
    table_id = scan.table_ids()[0]

    key_space_manifest: FragmentManifest = scan.key_space_scan(table_id).manifest
    _table_of_fragments(
        key_space_manifest,
        title="Key Space manifest",
    )

    for column_group in scan.column_groups():
        column_group_manifest: FragmentManifest = scan.column_group_scan(column_group).manifest
        _table_of_fragments(
            column_group_manifest,
            title=f"Column Group manifest for {str(column_group)}",
        )


def _table_of_fragments(manifest: FragmentManifest, title: str):
    """Display fragments in a formatted table."""
    # Calculate summary statistics
    total_size = sum(fragment.size_bytes for fragment in manifest)
    total_metadata_size = sum(len(fragment.format_metadata or b"") for fragment in manifest)
    fragment_count = len(manifest)
    avg_size = total_size / fragment_count if fragment_count > 0 else 0

    # Print title and summary
    print(f"\n\n{title}")
    print(
        f"{fragment_count} fragments, "
        f"total: {_format_bytes(total_size)}, "
        f"avg: {_format_bytes(int(avg_size))}, "
        f"metadata: {_format_bytes(total_metadata_size)}"
    )
    print("=" * 120)

    # Print header
    print(
        f"{'ID':<30} {'Size (Metadata)':<20} {'Format':<10} {'Key Span':<10} "
        f"{'Level':<5} {'Committed At':<20} {'Compacted At':<20}"
    )
    print("=" * 120)

    # Print each fragment
    for fragment in manifest:
        committed_str = str(datetime_.from_timestamp_micros(fragment.committed_at)) if fragment.committed_at else "N/A"
        compacted_str = str(datetime_.from_timestamp_micros(fragment.compacted_at)) if fragment.compacted_at else "N/A"

        size_with_metadata = (
            f"{_format_bytes(fragment.size_bytes)} ({_format_bytes(len(fragment.format_metadata or b''))})"
        )
        key_span = f"{fragment.key_span.begin}..{fragment.key_span.end}"

        print(
            f"{fragment.id:<30} "
            f"{size_with_metadata:<20} "
            f"{str(fragment.format):<10} "
            f"{key_span:<10} "
            f"{str(fragment.level):<5} "
            f"{committed_str:<20} "
            f"{compacted_str:<20}"
        )
