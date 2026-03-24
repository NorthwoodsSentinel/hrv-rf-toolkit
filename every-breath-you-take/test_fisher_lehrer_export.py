#!/usr/bin/env python3
"""
Test Script: Fisher & Lehrer RF Test with HRVisualizer Export

Quick test of the new export functionality without UI modifications.
Records a Fisher & Lehrer protocol session and exports to HRVisualizer format.

Usage:
    python test_fisher_lehrer_export.py [duration_minutes]

    duration_minutes: Optional, defaults to 15 (full protocol)
                     Use smaller value for testing (e.g., 2)
"""

import asyncio
import sys
from Model import Model
from sensor import SensorHandler


class RFTestSession:
    def __init__(self, duration_minutes=15):
        self.model = Model()
        self.sensor_handler = SensorHandler()
        self.duration_seconds = duration_minutes * 60
        self.protocol = "Fisher_Lehrer"

    async def run(self):
        """Run complete RF test session"""

        print("=" * 70)
        print("POLAR H10 RF TEST - FISHER & LEHRER PROTOCOL")
        print("=" * 70)

        # Scan for Polar H10
        print("\n🔍 Scanning for Polar H10...")
        await self.sensor_handler.scan()
        devices = self.sensor_handler.get_valid_device_names()

        if not devices:
            print("❌ No Polar H10 found!")
            return

        print(f"✅ Found: {devices[0]}")

        # Connect
        print(f"\n📡 Connecting to {devices[0]}...")
        sensor_client = self.sensor_handler.create_sensor_client(devices[0])
        await self.model.set_and_connect_sensor(sensor_client)
        print("✅ Connected!")

        # Configure protocol
        print(f"\n📋 Setting up {self.protocol} protocol...")
        self.model.protocol_manager.set_protocol(self.protocol)

        protocol_info = self.model.protocol_manager.protocols[self.protocol]
        print(f"   Name: {protocol_info['name']}")
        print(f"   Duration: {self.duration_seconds/60:.0f} minutes")
        print(f"   Breathing: {protocol_info['start_rate']:.2f} → {protocol_info['end_rate']:.2f} bpm")

        # Start session (sets recording timestamp)
        print(f"\n🫁 Starting session...")
        print(f"   Follow your breath naturally")
        print(f"   Breathing rate will automatically slide from 6.75 → 4.25 bpm")
        print(f"   Duration: {self.duration_seconds/60:.0f} minutes")
        print(f"\n⏱️  Session in progress... (Press Ctrl+C to stop early)\n")

        self.model.start_recording_session()

        # Progress tracking
        try:
            elapsed = 0
            while elapsed < self.duration_seconds:
                await asyncio.sleep(5)  # Update every 5 seconds
                elapsed += 5

                # Get current state
                info = self.model.protocol_manager.get_session_info()
                current_rate = self.model.protocol_manager.get_current_breathing_rate()

                # Show progress
                mins = int(info["elapsed"] // 60)
                secs = int(info["elapsed"] % 60)
                progress = int(info["progress"])

                print(f"   [{progress:3d}%] Time: {mins:02d}:{secs:02d} | "
                      f"Breathing: {current_rate:.2f} bpm | "
                      f"RR intervals: {len(self.model.hrv_analyser.ibi_history.values):4d} | "
                      f"Breaths: {len(self.model.breath_analyser.chest_acc_history.values):5d}")

                if info["is_complete"]:
                    break

        except KeyboardInterrupt:
            print("\n\n⏹️  Session stopped by user")

        # Stop session
        self.model.stop_recording_session()
        print("\n✅ Session complete!")

        # Show summary
        print("\n" + "=" * 70)
        print("SESSION SUMMARY")
        print("=" * 70)

        ibi_count = len([v for v in self.model.hrv_analyser.ibi_history.values if not sys.float_info.max])
        breath_count = len([v for v in self.model.breath_analyser.chest_acc_history.values if not sys.float_info.max])

        print(f"   RR intervals collected: {ibi_count}")
        print(f"   Breathing samples collected: {breath_count}")
        print(f"   Duration: {info['elapsed']/60:.2f} minutes")

        # Export
        print("\n" + "=" * 70)
        print("EXPORTING TO HRVISUALIZER")
        print("=" * 70)

        output_path = self.model.export_to_hrvisualizer(output_dir="exports")

        if output_path:
            print(f"\n🎉 SUCCESS!")
            print(f"\n📁 File saved: {output_path}")
            print(f"\n📝 Next steps:")
            print(f"   1. Transfer {output_path} to your Windows PC")
            print(f"   2. Open HRVisualizer")
            print(f"   3. Import the file")
            print(f"   4. Your RF will be displayed!")
        else:
            print("\n❌ Export failed (not enough data?)")

        # Disconnect
        print(f"\n📡 Disconnecting from Polar H10...")
        await self.model.disconnect_sensor()
        print("✅ Disconnected")

        print("\n" + "=" * 70)


async def main():
    """Main entry point"""

    # Parse duration from command line
    duration_minutes = 15  # Default: full protocol
    if len(sys.argv) > 1:
        try:
            duration_minutes = float(sys.argv[1])
            print(f"Using custom duration: {duration_minutes} minutes")
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}, using default 15 minutes")

    # Run session
    session = RFTestSession(duration_minutes=duration_minutes)
    await session.run()


if __name__ == "__main__":
    print("\n🔬 POLAR H10 RF DETERMINATION TEST")
    print("   Using Fisher & Lehrer (2022) protocol\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
