import asyncio
import time

async def run_single_command(cmd: str):
    """Run a single shell command asynchronously and log its execution time."""
    start_time = time.time()
    
    process = await asyncio.create_subprocess_shell(cmd)
    
    return_code = await process.wait()

    execution_time = time.time() - start_time
    if return_code != 0:
        print(f"  ❌ {cmd} failed with return code {return_code} ({execution_time:.1f}s)")
    else:
        print(f"  ✅ {cmd} completed in {execution_time:.1f}s")

async def run_command_group(group_name: str, commands: list[str]):
    """Run a group of commands asynchronously and log the total execution time."""
    start_time = time.time()

    tasks = [asyncio.create_task(run_single_command(cmd)) for cmd in commands]
    await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time
    print(f"✅ {group_name} completed in {total_time:.1f}s")

async def run_with_staged_execution():
    """Run the entire pipeline with staged execution and parallel tasks where applicable."""
    overall_start = time.time()

    print("\nStarting Stage 1 - Initial Processing...")
    await run_command_group("Stage 1 - Initial Processing", [
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
    print(f"✅ Stage 2 - Pro and Optimole Mailbox Operations completed in {time.time() - overall_start:.1f}s")

    print("\n🔄 Starting Stage 3 - Remaining Tasks...")
    await run_command_group("Stage 3 - Remaining Tasks", [
        "python FilterMailboxes/filter_wporg_conversations.py",
        "python FilterMailboxes/filter_optimole_conversations.py"
    ])
    
    print("\n🔄 Starting Stage 4...")
    await run_single_command("python HelperFiles/helper_file_to_see_no_replies_emails_in_optimole.py")

    print("\n🔄 Starting Stage 5 - Sequential Final Processing...")
    await run_single_command("python ProcessMailboxes/process_optimole_conversations.py")
    await run_single_command("python ProcessMailboxes/process_wporg_conversations.py")

    print(f"\n🎉 Pipeline completed in {time.time() - overall_start:.1f}s")

async def main():
    await run_with_staged_execution()

if __name__ == "__main__":
    asyncio.run(main())