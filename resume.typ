// Edit this document directly. CI runs `typst compile` to produce the PDF.
#set document(title: "Amar Chandra Resume", author: "Amar Chandra")
#set page("us-letter", margin: (x: 0.5in, y: 0.5in))
#set text(font: "Carlito", size: 10.5pt, top-edge: 0.75em, bottom-edge: -0.25em, ligatures: false)
#set par(leading: 2.32pt, spacing: 2.32pt, justify: false)
#set smartquote(enabled: false)
#set list(indent: 18pt, body-indent: 0pt, marker: box(width: 18pt)[#circle(radius: 2.25pt, fill: black)], marker-align: left, spacing: 2.32pt)
#show link: it => underline(text(fill: rgb("#1155cc"), it))

#let section(title, gap: 19.3pt) = block(
  width: 100%, above: gap, below: 5.8pt,
  stroke: (bottom: 0.75pt), inset: (bottom: 1.5pt),
)[#text(size: 12pt, weight: "bold", bottom-edge: "baseline")[#title]]
#let row(left, right) = block(below: 2.32pt)[#left#h(1fr)#right]
#let project(title, url, tools) = block(above: 4.32pt, below: 2.32pt)[#link(url)[*#title*] | #emph(tools)]

#v(3.5pt)
#align(center)[
  #text(size: 16pt, weight: "bold")[Amar Chandra]
  #v(0.05pt)
  chandra.ama\@northeastern.edu | (516)-522-8604 | #link("http://linkedin.com/in/AmarsChandra")[linkedin.com/in/AmarsChandra] | #link("http://github.com/AmarsChandra")[github.com/AmarsChandra]
]

#section("EDUCATION", gap: 2.6pt)
#row([*Northeastern University*], [*Boston, Massachusetts*])
#row([_B.S. in Computer Science, Concentration in Software_], [_Expected May 2028_])
- *GPA:* 3.80/4.00 | Dean’s List
- *Related Coursework:* Algorithms & Data, Computer Systems, Network Fundamentals, Object-Oriented Design, Foundations of Data Science, Linear Algebra

#section("EXPERIENCE")
#row([*Chewy*], [*Boston, Massachusetts*])
#row([_Software Engineering Co-op_], [_Jun 2026 – Dec 2026_])
- Developed Python backend APIs supporting promotion creation, SKU configuration, and customer segmentation workflows for Chewy's internal promotion-management platform
- Built the Promo Details interface in React, TypeScript, and Next.js from Figma designs, and integrated backend APIs across the Promo Details and Intake Details screens using TanStack React Query
- Migrated a Vendor Partner Portal API dashboard from Datadog to Dynatrace, monitoring nine user-facing routes across development, testing, staging, and production

#row([*Northeastern Electric Racing*], [*Boston, Massachusetts*])
#row([_Embedded Software Engineer_], [_Sep 2025 – Present_])
#set list(spacing: 4.32pt)
- Develop embedded firmware for the tractive system controller using C on STM32 microcontrollers
- Collaborate in an Agile software team using GitHub for version control, code reviews, and issue tracking

#section("PROJECTS", gap: 21.3pt)
#project("Nest: Undisclosed Ad Blocker", "https://chromewebstore.google.com/detail/nest/lccmhgnmbohapbifjmfahachedenmehh", "JavaScript, Chrome Extensions, Machine Learning")
- Developed a Chrome extension using a custom-trained image detection model to identify and remove undisclosed gambling advertisements from X in real-time
- Implemented DOM monitoring with MutationObserver, debounced event handling, and periodic fallback scans to detect dynamically loaded content while maintaining responsive browsing performance
- Earned a 4.8 star rating on the Chrome Web Store from *200+ users*, reflecting strong user satisfaction and reliability

#project("Pilot: Bulk Social Media Scheduler", "https://github.com/AmarsChandra/pilot-private", "TypeScript, React, Next.js, Express")
- Developed a full-stack application that bulk schedules Buffer posts from folders, ZIP archives, and Reddit content, automating media uploads, caption pairing, and multi-channel publishing
- Integrated the Buffer GraphQL API, Cloudinary, and Reddit APIs to support batch scheduling, subreddit image discovery, recurring posts, approval workflows, and queue management
- Engineered an Express backend with rate-limit handling, request validation, caching, and resilient file-processing pipelines capable of ingesting up to 2,000 uploaded assets per batch

#project("AI Github PR Reviewer", "https://github.com/AmarsChandra/amars-bugbot", "Python, FastAPI, GitHub API, OpenAI API")
- Developed an AI-powered GitHub pull request reviewer that automatically analyzes code changes and generates contextual feedback using large language models
- Integrated GitHub webhooks, the GitHub API, and OpenAI APIs to review pull requests, summarize code changes, and surface potential bugs and code-quality issues
- Engineered an asynchronous review pipeline with repository cloning, diff parsing, and configurable review prompts to automate code review workflows

#section("TECHNICAL SKILLS")
*Languages:* Java, Python, TypeScript, JavaScript, C, SQL, HTML/CSS \
*Frameworks & Libraries:* React, Next.js, FastAPI, TanStack React Query, Jest, React Testing Library, scikit-learn, pandas, NumPy \
*Developer Tools:* Git, GitHub, Docker, Linux/Unix, Vercel, Firebase, Supabase, STM32 \
*Technologies:* REST APIs, GraphQL, Chrome Extensions, Webhooks, LLMs, TLS/SSL
