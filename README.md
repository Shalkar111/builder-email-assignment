# Assignment 1: Builder Pattern - Email

**Student:** Шалкар | **Group:** SE-2532

**GitHub:** https://github.com/Shalkar111/builder-email-assignment

Java 17-compatible console project with no external libraries. The same four
steps (`setFrom`, `setTo`, `setSubject`, `setBody`) produce either an immutable
`Email` object or a text preview. No email is actually sent.

## Open in IntelliJ IDEA

1. Choose **File > Open** and select this project folder.
2. Select an installed **JDK 17 or newer** in **File > Project Structure > Project**
   if IDEA asks for an SDK. This Mac already has JDK 24 configured.
3. Open `src/main/java/assignment/builder/Main.java`.
4. Click the green run triangle next to `main`, or run **Email Demo**.

No Maven, Gradle, downloads or plugins are needed for the Java program.

## Run and check from a terminal

```bash
bash run.sh
bash test.sh
```

The scripts compile with `--release 17`, UTF-8 and all compiler warnings treated
as errors. The check runner reports **PASS: 64 behavioral checks.** Compilation
and execution were verified using JDK 24.0.1 targeting Java 17.

## Pattern roles

| Role | Class | Purpose |
| --- | --- | --- |
| Product | `Email` | Immutable snapshot with four final String fields |
| Builder interface | `EmailBuilder` | Shared fluent construction steps |
| Concrete builder | `EmailObjectBuilder` | `getResult()` returns `Email` |
| Concrete builder | `EmailPreviewBuilder` | `getResult()` returns `String` |
| Director | `EmailDirector` | Welcome and order-confirmation recipes |
| Internal helper | `EmailDraft` | Mutable construction state and shared validation |
| Client | `Main` | Applies both recipes to both builders and prints results |

`getResult()` stays on the concrete builders because their return types differ.
The director accepts only `EmailBuilder` and never inspects a concrete result.
Each builder owns its own draft; they share the helper class, not one instance.
The package-private one-argument `Email` constructor copies values from the
draft and does not retain the mutable draft.

## Validation and builder reuse

Both `getResult()` methods reject missing/blank fields, malformed sender or
recipient addresses, and multiline subjects with `IllegalStateException`.
Bodies may contain multiple lines. Address checking is intentionally a small
classroom rule; it does not implement the full Internet email specification.

Calling a step again replaces its value. Calling `getResult()` again is safe.
Builders retain their current values until overwritten; both director recipes
set all four fields. Existing products stay unchanged after builder edits.
Builders are mutable and intended for use by one thread.

## Example

```java
EmailDirector director = new EmailDirector();
EmailObjectBuilder objectBuilder = new EmailObjectBuilder();
EmailPreviewBuilder previewBuilder = new EmailPreviewBuilder();

director.makeWelcomeEmail(objectBuilder);
director.makeWelcomeEmail(previewBuilder);

Email email = objectBuilder.getResult();
String preview = previewBuilder.getResult();
System.out.println(preview);
```

```text
=== Email Preview ===
From: support@example.com
To: customer@example.com
Subject: Welcome to Study Shop

Hello! Your account is ready. Thank you for joining Study Shop.
```

## Report and defense

- `output/pdf/Assignment_1_Builder_Report.pdf`: report with UML and seven Clean Code examples.
- `docs/report.md`: editable text of the report.
- `docs/uml.puml`: editable UML source.
- `docs/DEFENSE_RU.md`: explanation and practice questions in Russian.
- `docs/SUBMISSION_RU.md`: GitHub/Moodle handoff steps and remaining publication status.

The Java program does not require Python. To regenerate only the report, install
ReportLab for Python and run `python3 docs/make_report.py`. After publication,
run it with `--github-url` followed by the real HTTPS repository URL. The script
uses macOS fonts when available and supports DejaVu fonts on Linux.

## Git history

The project was developed in four incremental local commits by Codex. GitHub
uploads are separate publication commits, grouped by implementation stage;
their dates and authors are not presented as the original development history.
`development-history.bundle` preserves all four original commits, including
their exact hashes, parent relationships and source snapshots. To inspect them:

```bash
git clone development-history.bundle original-development
git -C original-development log --oneline
```

The bundle captures the original development before the repository URL was added.
The ordinary files in this repository contain the current submission version.
