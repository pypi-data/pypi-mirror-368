#!/usr/bin/env python3
# this_file: external/int_folders/d361/scripts/monitor_d360_api.py
"""
Standalone script to monitor Document360 API changes and auto-update models.

This script provides monitoring capabilities for the Document360 OpenAPI
specification, automatically regenerating Pydantic models when changes
are detected.

Usage:
    python monitor_d360_api.py [COMMAND] [OPTIONS]

Commands:
    run         Run one-time update check
    monitor     Start continuous monitoring (background service)
    status      Show current monitoring status

Examples:
    # Run one-time update
    python monitor_d360_api.py run --force
    
    # Start monitoring with 30 minute intervals
    python monitor_d360_api.py monitor --check_interval_seconds 1800
    
    # Check status
    python monitor_d360_api.py status
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the path so we can import d361
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))


async def run_update(output_dir: str = "generated/models", force: bool = False):
    """Run a one-time update check and model generation."""
    from d361.api.api_updater import run_one_time_update
    
    print(f"🔍 Checking for Document360 API updates...")
    if force:
        print("   (forcing update regardless of changes)")
    
    event = await run_one_time_update(output_dir=output_dir, force=force)
    
    if event.status.value == "success":
        print(f"✅ Update completed successfully!")
        print(f"   Files updated: {len(event.files_updated)}")
        for file_path in event.files_updated:
            print(f"   - {file_path}")
        if event.changes_detected:
            print(f"   Changes detected:")
            for change in event.changes_detected:
                print(f"   - {change}")
    elif event.status.value == "skipped":
        print(f"⏭️  No changes detected - skipping update")
    else:
        print(f"❌ Update failed!")
        for error in event.errors:
            print(f"   Error: {error}")


async def start_monitoring(
    output_dir: str = "generated/models",
    check_interval_seconds: int = 3600,
    auto_update: bool = True
):
    """Start continuous monitoring for API changes."""
    from d361.api.api_updater import create_updater
    
    print(f"🔄 Starting Document360 API monitoring...")
    print(f"   Check interval: {check_interval_seconds} seconds")
    print(f"   Auto-update: {'enabled' if auto_update else 'disabled'}")
    print(f"   Output directory: {output_dir}")
    print()
    print("Press Ctrl+C to stop monitoring")
    
    # Create callbacks for logging
    def on_update_start(event):
        print(f"🚀 Starting update (trigger: {event.trigger})")
    
    def on_update_complete(event):
        print(f"✅ Update completed successfully!")
        print(f"   Duration: {event.duration_seconds:.1f}s")
        print(f"   Files updated: {len(event.files_updated)}")
    
    def on_update_failed(event):
        print(f"❌ Update failed!")
        for error in event.errors:
            print(f"   Error: {error}")
    
    callbacks = {
        'on_update_start': on_update_start,
        'on_update_complete': on_update_complete,
        'on_update_failed': on_update_failed
    }
    
    updater = await create_updater(
        output_dir=output_dir,
        check_interval_seconds=check_interval_seconds,
        auto_update=auto_update,
        callbacks=callbacks
    )
    
    try:
        await updater.start_monitoring()
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        await updater.stop_monitoring()
        await updater.close()
        print("✅ Monitoring stopped")


async def show_status():
    """Show current monitoring status."""
    from d361.api.api_updater import create_updater
    
    updater = await create_updater()
    
    try:
        status = updater.get_status()
        history = updater.get_update_history(limit=5)
        
        print("📊 API Updater Status")
        print(f"   Running: {'🟢 Yes' if status['running'] else '🔴 No'}")
        print(f"   Auto-update: {'🟢 Enabled' if status['auto_update_enabled'] else '🔴 Disabled'}")
        print(f"   Check interval: {status['check_interval_seconds']} seconds")
        print(f"   Current spec hash: {status['current_spec_hash'][:8] if status['current_spec_hash'] else 'None'}")
        print(f"   History entries: {status['history_count']}")
        
        if status['last_update']:
            print(f"   Last update: {status['last_update']}")
        
        if history:
            print("\n📈 Recent Update History")
            for i, event in enumerate(history):
                status_icon = {
                    'success': '✅',
                    'failed': '❌',
                    'skipped': '⏭️',
                    'pending': '⏳',
                    'running': '🔄'
                }.get(event.status.value, '❓')
                
                print(f"   {i+1}. {status_icon} {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {event.status.value} ({event.trigger.value})")
                if event.duration_seconds:
                    print(f"      Duration: {event.duration_seconds:.1f}s")
        
    finally:
        await updater.close()


def main():
    """Main CLI interface."""
    import fire
    
    class MonitorCLI:
        """CLI interface for Document360 API monitoring."""
        
        def run(self, output_dir: str = "generated/models", force: bool = False):
            """Run one-time update check."""
            return asyncio.run(run_update(output_dir=output_dir, force=force))
        
        def monitor(
            self,
            output_dir: str = "generated/models",
            check_interval_seconds: int = 3600,
            auto_update: bool = True
        ):
            """Start continuous monitoring."""
            return asyncio.run(start_monitoring(
                output_dir=output_dir,
                check_interval_seconds=check_interval_seconds,
                auto_update=auto_update
            ))
        
        def status(self):
            """Show monitoring status."""
            return asyncio.run(show_status())
    
    fire.Fire(MonitorCLI)


if __name__ == "__main__":
    main()