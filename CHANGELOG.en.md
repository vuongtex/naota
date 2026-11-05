# Changelog

*[Tiếng Việt](CHANGELOG.md) · **English***

NAOTA release history. Newest first.

## [1.8.0] - 2026-11-05
### Security
- **Several leaks closed after a review:** chatbots and background work below Full access can no longer write where code runs, scheduled jobs cannot exceed their maker's level, HTML files opened from the brain run in a sandbox, and other pages on the machine cannot send commands into NAOTA.
### Added
- **A new Models page:** Disconnect on every card, OpenAI Compatible and Claude Compatible take several keys and switch when one runs out, and Antigravity on a VPS can add accounts (not yet tried with a real `agy`).
- **Naota Core edits like any assistant** and can have its own name per brain. **One bot serves up to 100 Facebook Pages.** The Avatar has a menu you arrange, and a voice call from an assistant's chat speaks as that assistant.
### Improved
- **Background work on an API key runs to the end**, up to 500 tool rounds, with a real terminal at Full access. **Chat can edit every task and appointment** in your to-do list.
- **Faster and lighter:** switching chats, Tasks, Teams and Assistants is instant, the speak-to-type mic reaches the customer reply box, Enter sends, and Android no longer repeats words.

## [1.7.0] - 2026-11-05
### Added
- **My tasks gets a daily pulse**: a Clean day streak, a star on up to 3 priorities, Skip this time for repeats, Move and Delete icons on each row (Undo if you delete by mistake), and a word of praise when you finish.
- **A long answer rings your phone**: from 3 minutes up the bell rings, unless the device is open. A background command reports to the right chat when it ends and carries on with what was planned.
### Improved
- **Scheduled jobs made in a partner chat** report to that chat and run as that assistant, and failures go back there too. Jobs made earlier run as before. Schedules on Codex can now hand work to a Team.
- **The inbox opens a chat at once** and loads only what is new. **Claude plan names are right** per vendor (Ultra, for example).

## [1.6.1] - 2026-11-04
### Added
- **Edit Agent button in the Chatbot form**: edit the bot's Agent on the spot, and what you typed in the form stays.
### Fixed
- **Rules taught to an assistant in chat now reach its bot**: at every permission level, with no need to copy them into the Agent file.
- **Bots read Zalo contact cards**: when a customer sends one, the bot and the inbox see the name and phone number.
- **Read only, Reads documents and Can write bots know the current time**: asked about today or opening hours, the bot no longer has to guess.

## [1.6.0] - 2026-11-04
### Added
- **Threads on the Meta connection card**: replies under your Threads posts reach the inbox and the bot can answer publicly. Each account picks off, inbox only, or bot replies. Threads only lets you hide a reply, not delete it, so NAOTA says that and asks first.
- **Teams do more**: attach a GitHub repo (edits on its own branch, opens a PR, red CI gets at most 3 fix rounds), call `/skill` in the team chat, and members open a job when given one in the chat, at most 5 a day by default.
- **My tasks get Tags and subtasks**: old Projects become tags, nothing is lost. Notes can link to pages, `[[notes]]` and files.
- **Internal API channel (experimental)**: one of your servers asks a Chatbot over HTTP. The key shows once, the bot only reads, and by default only the machine running NAOTA can call it.

### Improved
- **Drag to reorder** projects, pinned chats and tags, the same order on every device. The Naota Core card says which model it runs on and can pick one. Phones get an **Install on phone** button in the menu.
- **Claude Code waits for background work** before it carries on, up to 30 minutes. The answer to a message added mid-turn shows right below it. Antigravity no longer warns by mistake that it could not read the context file.

## [1.5.0] - 2026-11-04
### Added
- **Message a commenter privately** from their comment thread: pick Reply publicly or Message privately above the box. Meta allows one per comment, within 7 days.
- **Instagram in the shared inbox**: tick "Also connect the Page's Instagram" when connecting, and Instagram messages and comments arrive in the same place, with the same bot as the Page.
- **The "..." menu on each chat** now has View profile, Block and Delete chat. NAOTA always asks before Delete, because deleting a comment or a personal Zalo chat really deletes it there.

### Improved
- The Facebook Messenger card is now **Meta connection**, with an icon for each app and a **Disconnect** button on each Page. Past chats stay. Comments and Instagram get their own icons in the inbox.

## [1.4.0] - 2026-11-03
### Added
- **Pick a time zone** in **Settings** (the Language and time zone block) and in the last step of first-run setup. "Today", "yesterday", reminders and report numbers follow it, even when the server runs on UTC. The default is Vietnam time.

### Fixed
- **No more freezing while NAOTA is answering**, and no more "Reconnecting" over and over on a slow device or network.
- **A small server (1-2 vCPU VPS) no longer stalls** because a few slow jobs blocked the whole app. The voice-note listener leaves one core to the server.
- **The Claude 5-hour limit notice shows the reset time in your time zone**, not UTC.
- Windows: `npx` connections no longer break when a path has a space, and `/C:/...` links in answers open.

### Improved
- **New Claude Code chats use less of your plan limit**: the system prompt stays identical between chats, so it is read back from the cache.
- Tables with 4 or more columns in Chat get more width on a computer, while ordinary text keeps an easy line length.

## [1.3.6] - 2026-11-03
### Fixed
- **On a phone, the Update button at the foot of the menu closes the menu**, so the Update page shows right away. The page used to change behind a menu that stayed open.
- **Tapping Advanced on a phone no longer closes the menu**, so the items inside can be picked.

## [1.3.4] - 2026-11-03
### Fixed
- **The Zalo bot notices when it is tagged in a group by the account's Zalo name**, even right after a server restart. NAOTA used to forget that name on every restart, so a tag that did not match the connection name got no answer.

## [1.3.3] - 2026-11-03
### Fixed
- **The Chatbot page names the brain you picked**, instead of the word "brain" or a folder path.

## [1.3.2] - 2026-11-03
### Improved
- **Page titles match the sidebar names**: Brain map, Tasks, Partners, Connections, Models.
- **On phones the brain picker sits at the top of the menu**, so you see which brain you are in as soon as you open it.

## [1.3.1] - 2026-11-03
### Improved
- Version number only. The two changes meant for this release are in 1.3.2.

## [1.3.0] - 2026-11-03
### Improved
- **A new one-column sidebar**: items in blocks with small names (Team, Knowledge, Connections, System).
- **Plainer item names in the sidebar** (Vietnamese interface): brain map, chat, to-do, assistants, data connections, model picker.
- **The version and an Update button always show at the foot of the sidebar**; the button turns yellow when a new version is out.
- **Advanced sits under Account** and unfolds Terminal, Plugins, Webhooks, Logins, Share links and the NAOTA community. Language is picked in Settings. Pages and the top bar stay as in 1.2.1.

## [1.2.1] - 2026-11-03
### Improved
- **The Store has Naota Gate**: ChatGPT and Claude connect to Naota through one pack, read and post into your chats, and keep a log. Machines with the **Naota in ChatGPT** pack see Gate as an update, no need to reconnect.
- **14 Store packs now have English ids**, for example Customer management is `naota.crm`. Installed packs show **Update available** and update in place, keeping their data.

## [1.2.0] - 2026-11-03
### Added
- **ChatGPT and Claude keep a log in Naota.** When you work something out with an outside AI connected to Naota, it notes what you said, what you decided and why. Naota keeps the context and remembers your decisions, at no cost in Naota runs.
### Improved
- The **Learn** page names **NAOTA** throughout: sync NAOTA with GitHub, NAOTA learns from your chats, what NAOTA has learned.

## [1.1.1] - 2026-11-03
### Fixed
- **The phone menu no longer overlaps.** The last items (Connections, Store, System...) used to spill over the language, brain picker and version rows. Everything now sits in order; scroll down to reach it.

## [1.1.0] - 2026-11-02
### Added
- **Desktop installers.** Download Naota-Setup.exe (Windows) or Naota-macOS.dmg (Mac) and open it like any app, no commands to type.
- **Connect a Facebook Page once for three jobs:** press Log in with Facebook and the bot answers Messenger messages, replies to comments under posts, and Naota posts to the Page now or on a schedule. A step-by-step guide is included.
- **Voice messages without Groq:** use an OpenAI or Gemini key, or a listener that runs on the machine itself. The personal Zalo chatbot hears voice messages and looks at videos customers send.
- **Outside AI can hand Naota work:** find, read and send a message into a Naota conversation as if you typed it, which you can watch live and stop at any time.
### Improved
- **Answers appear as they are written** on every brain: Claude Code, Grok Build, Antigravity and the API key brains.
- **Redesigned Webhook page:** a one-line overview, each webhook opens in its own window, and workflows can be searched by name.
- **Brain picker** drawn by Naota, the same on every device, with your own order. An .html file opens on its live page with the code one tab away. A long paste shows a preview first, then you choose to paste or attach it.
- **Teams retry** a step that hit a temporary error, and each part of a plan states which parts it waits for.
### Fixed
- Claude sign-in finishes on its own on a machine with a browser, no code needed. Dropping a file on the main chat works again, memory recall no longer picks up old run logs, and accented file names stay intact on download.
## [1.0.5] - 2026-11-02
### Fixed
- **The Update button on a VPS no longer waits forever.** When the server runs NAOTA as a normal user that may not update itself, the page now shows the error at once, with the manual update command and how to enable the button, instead of waiting 10 minutes and asking for a reload.

## [1.0.4] - 2026-11-02
### Improved
- **New icon set** across the sidebar and the whole app.
- **Mascot** is now called **Avatar**.
- **Updates** has its own sidebar item right under **Account**, with a **New** badge when a newer version is out.
- Leftover "brain" wording in the interface, the Plugins page and the Learn page now reads clearly: brain means your notes vault, AI model means Claude, ChatGPT and the like.

## [1.0.3] - 2026-11-02
### Improved
- The Account and Settings name block and the Models main-card badge now come from translations (Vietnamese: Tên NAOTA, Chính).

## [1.0.2] - 2026-11-02
### Improved
- **One name for the store** in Vietnamese: the Agents, Data sources and Plugins pages now match the sidebar.
- **Fewer English terms in Vietnamese** on the Learn, Models and Account pages. The account name field reads **Your NAOTA name**.

## [1.0.1] - 2026-11-02
### Improved
- **A tidier sidebar.** Every item shows at once, no groups to open. Rarely used pages sit in a folded **Advanced** group and **System** is pinned to the bottom.
- **Clearer menu names** in Vietnamese. Voice commands accept the new names too.
- **A plainer welcome screen.** Pick a brain by the plan you already have, then click **Sign in with Claude** on the **Models** page, no terminal command needed.
- **Home page labels** are translated in Vietnamese (vault, agents, skills, workflows, note counts).
## [1.0.0] - 2026-10-31
### Added
- **NAOTA is born.** Your own AI brain, built by Hoang Ngoc Vuong for the NAOTA community.
