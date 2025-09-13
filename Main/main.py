import asyncio
import time

async def run_single_command(cmd: str):
    start_time = time.time()

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    execution_time = time.time() - start_time
    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        print(f"  ❌ {cmd} failed ({execution_time:.1f}s): {error_msg}")
    else:
        print(f"  ✅ {cmd} completed in {execution_time:.1f}s")

async def run_command_group(group_name: str, commands: list[str]):
    start_time = time.time()

    tasks = [asyncio.create_task(run_single_command(cmd)) for cmd in commands]
    await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time
    print(f"✅ {group_name} completed in {total_time:.1f}s")

async def run_with_staged_execution():
    overall_start = time.time()

    await run_command_group("Stage 1 - Free Mailbox Operations", [
        "python HelpscoutMailboxes/helpscout_free_mailbox.py",
        "python HelpscoutMailboxes/helpscout_free_mailbox_tags.py"
    ])

    print("\n🔄 Starting Stage 2 - Pro and Optimole Mailbox Operations...")

    async def pro_chain():
        await run_single_command("python HelpscoutMailboxes/helpscout_pro_mailbox.py")
        await run_single_command("python ProcessMailboxes/process_pro_conversations.py")

    stage2_tasks = [
        asyncio.create_task(run_single_command("python HelpscoutMailboxes/helpscout_optimole_mailbox.py")),
        asyncio.create_task(pro_chain())
    ]
    await asyncio.gather(*stage2_tasks, return_exceptions=True)

    await run_command_group("Stage 3 - Remaining Tasks", [
        "python FilterMailboxes/filter_wporg_conversations.py",
        "python FilterMailboxes/filter_optimole_conversations.py"
    ])

    await run_command_group("Stage 4 - Final Processing", [
        "python HelperFiles/helper_file_to_see_no_replies_emails_in_optimole.py",
        "python ProcessMailboxes/process_optimole_conversations.py",
        "python ProcessMailboxes/process_wporg_conversations.py",
    ])

    print(f"\n🎉 Pipeline completed in {time.time() - overall_start:.1f}s")

async def main():
    await run_with_staged_execution()

if __name__ == "__main__":
    asyncio.run(main())