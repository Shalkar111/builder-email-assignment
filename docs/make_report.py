#!/usr/bin/env python3
"""Generate the PDF and editable Markdown from real project code excerpts."""

import argparse
import math
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/main/java/assignment/builder"
OUTPUT = ROOT / "output/pdf/Assignment_1_Builder_Report.pdf"
WIDTH, HEIGHT = A4
MARGIN = 46
CONTENT = WIDTH - 2 * MARGIN
NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#087F8C")
INK = colors.HexColor("#263340")
MUTED = colors.HexColor("#5C6875")
PALE = colors.HexColor("#F2F6F9")


def register_fonts():
    families = [
        (Path("/System/Library/Fonts/Supplemental"),
         ("Arial.ttf", "Arial Bold.ttf", "Courier New.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu"),
         ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf")),
    ]
    for base, names in families:
        if all((base / name).exists() for name in names):
            for alias, name in zip(("Body", "BodyBold", "Code"), names):
                pdfmetrics.registerFont(TTFont(alias, str(base / name)))
            pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyBold")
            return
    raise RuntimeError("Install Arial or DejaVu fonts to render the report.")


def excerpt(filename, start, end):
    lines = (SOURCE / filename).read_text().splitlines()
    first = next(i for i, line in enumerate(lines) if start in line)
    last = next(i for i in range(first, len(lines))
                if (lines[i] == end if end.strip() == "}" else end in lines[i]))
    selected = lines[first:last + 1]
    indent = min(len(line) - len(line.lstrip()) for line in selected if line.strip())
    return "\n".join(line[indent:] for line in selected), f"{filename}, lines {first + 1}-{last + 1}"


class Report:
    def __init__(self, github_url):
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        self.pdf = canvas.Canvas(str(OUTPUT), pagesize=A4)
        self.pdf.setTitle("Assignment 1 - Builder Pattern: Email")
        self.pdf.setAuthor("Шалкар, SE-2532")
        self.github_url = github_url
        self.page = 0
        self.y = HEIGHT - MARGIN
        self.markdown = ["# Assignment 1: Builder Pattern - Email\n",
                         "**Student:** Шалкар | **Group:** SE-2532\n"]
        self.body_style = ParagraphStyle("Body", fontName="Body", fontSize=10.1,
                                         leading=14.7, textColor=INK, alignment=TA_LEFT)

    def reserve(self, height):
        if self.y - height < 58:
            raise RuntimeError(f"Page {self.page} overflow: y={self.y}, block={height}")

    def new_page(self, title, subtitle=None):
        if self.page:
            self.pdf.showPage()
        self.page += 1
        self.y = HEIGHT - 66
        p = self.pdf
        p.setFillColor(TEAL)
        p.rect(MARGIN, HEIGHT - 39, 30, 3, fill=1, stroke=0)
        p.setFillColor(MUTED)
        p.setFont("Body", 8)
        p.drawString(MARGIN + 40, HEIGHT - 40, "ASSIGNMENT 1 / BUILDER PATTERN / EMAIL")
        p.setStrokeColor(colors.HexColor("#D9E1E8"))
        p.line(MARGIN, 42, WIDTH - MARGIN, 42)
        p.setFont("Body", 8)
        p.drawString(MARGIN, 28, "Шалкар  |  SE-2532  |  12 September 2026")
        p.drawRightString(WIDTH - MARGIN, 28, str(self.page))
        self.heading(title, large=True)
        if subtitle:
            self.paragraph(subtitle, small=True)

    def heading(self, text, large=False):
        size = 23 if large else 12.5
        height = 36 if large else 24
        self.reserve(height)
        self.pdf.setFont("BodyBold", size)
        self.pdf.setFillColor(NAVY)
        self.pdf.drawString(MARGIN, self.y - size, text)
        self.y -= height
        self.markdown.append(f"{'##' if large else '###'} {text}\n")

    def paragraph(self, text, small=False, record=True):
        style = self.body_style
        if small:
            style = ParagraphStyle("Small", parent=style, fontSize=8.7, leading=12.5,
                                   textColor=MUTED)
        para = Paragraph(escape(text), style)
        _, height = para.wrap(CONTENT, 1000)
        self.reserve(height + 10)
        para.drawOn(self.pdf, MARGIN, self.y - height)
        self.y -= height + 10
        if record:
            self.markdown.append(text + "\n")

    def code(self, code, label):
        size, leading = 8.2, 11.2
        lines = code.splitlines()
        if any(pdfmetrics.stringWidth(line, "Code", size) > CONTENT - 20 for line in lines):
            raise RuntimeError(f"Code line too wide: {label}")
        height = len(lines) * leading + 16
        self.reserve(height + 27)
        self.pdf.setFillColor(PALE)
        self.pdf.roundRect(MARGIN, self.y - height, CONTENT, height, 4, fill=1, stroke=0)
        self.pdf.setFillColor(INK)
        self.pdf.setFont("Code", size)
        for i, line in enumerate(lines):
            self.pdf.drawString(MARGIN + 10, self.y - 15 - i * leading, line)
        self.y -= height + 4
        self.paragraph(label, small=True, record=False)
        self.markdown.append(f"```java\n{code}\n```\n\nSource: {label}\n")

    def table(self, rows):
        style = ParagraphStyle("Cell", parent=self.body_style, fontSize=9.1, leading=12.4)
        cells = [[Paragraph(escape(str(cell)), style) for cell in row] for row in rows]
        table = Table(cells, colWidths=[152, CONTENT - 152], hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E4EDF3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        _, height = table.wrap(CONTENT, 1000)
        self.reserve(height + 14)
        table.drawOn(self.pdf, MARGIN, self.y - height)
        self.y -= height + 14
        self.markdown.extend(["| " + " | ".join(row) + " |" for row in rows[:1]])
        self.markdown.append("| --- | --- |")
        self.markdown.extend(["| " + " | ".join(row) + " |" for row in rows[1:]])
        self.markdown.append("")

    def uml(self):
        self.reserve(547)
        p = self.pdf
        p.saveState()
        p.translate(MARGIN, self.y - 525)

        def box(x, y, width, title, attributes, methods, tag=""):
            header = 37 if tag else 24
            attr_height = len(attributes) * 11 + 10 if attributes else 0
            method_height = len(methods) * 11 + 12
            height = header + attr_height + method_height
            p.setFillColor(colors.white)
            p.setStrokeColor(NAVY)
            p.setLineWidth(0.8)
            p.rect(x, y, width, height, fill=1, stroke=1)
            p.setFillColor(PALE)
            p.rect(x + 0.5, y + height - header, width - 1, header - 0.5, fill=1, stroke=0)
            p.setFillColor(NAVY)
            p.setFont("BodyBold", 10)
            p.drawCentredString(x + width / 2, y + height - 16, title)
            if tag:
                p.setFont("Body", 8)
                p.drawCentredString(x + width / 2, y + height - 29, tag)
            divider = y + height - header
            p.line(x, divider, x + width, divider)
            cursor = divider - 13
            p.setFont("Code", 7.6)
            p.setFillColor(INK)
            for line in attributes:
                p.drawString(x + 8, cursor, line)
                cursor -= 11
            if attributes:
                p.line(x, divider - attr_height, x + width, divider - attr_height)
                cursor = divider - attr_height - 13
            for line in methods:
                if pdfmetrics.stringWidth(line, "Code", 7.6) > width - 16:
                    raise RuntimeError("UML label too wide: " + line)
                p.drawString(x + 8, cursor, line)
                cursor -= 11
            return height

        def connector(points, kind="dependency", label=None, label_at=None):
            p.setStrokeColor(MUTED)
            p.setFillColor(MUTED)
            p.setLineWidth(0.8)
            p.setDash(3, 2) if kind in ("dependency", "realization") else p.setDash()
            path = p.beginPath()
            path.moveTo(*points[0])
            for point in points[1:]:
                path.lineTo(*point)
            p.drawPath(path)
            p.setDash()
            tip = points[-1]
            prev = points[-2]
            theta = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
            ux, uy = math.cos(theta), math.sin(theta)
            if kind in ("dependency", "realization"):
                length, half = (9, 4) if kind == "realization" else (6, 3)
                a = (tip[0] - length * ux - half * uy, tip[1] - length * uy + half * ux)
                b = (tip[0] - length * ux + half * uy, tip[1] - length * uy - half * ux)
                head = p.beginPath()
                head.moveTo(*a)
                head.lineTo(*tip)
                head.lineTo(*b)
                if kind == "realization":
                    head.close()
                    p.setFillColor(colors.white)
                    p.drawPath(head, fill=1, stroke=1)
                else:
                    p.drawPath(head)
            else:
                start, second = points[:2]
                theta = math.atan2(second[1] - start[1], second[0] - start[0])
                ux, uy = math.cos(theta), math.sin(theta)
                diamond = p.beginPath()
                diamond.moveTo(*start)
                diamond.lineTo(start[0] + 5 * ux - 3 * uy, start[1] + 5 * uy + 3 * ux)
                diamond.lineTo(start[0] + 10 * ux, start[1] + 10 * uy)
                diamond.lineTo(start[0] + 5 * ux + 3 * uy, start[1] + 5 * uy - 3 * ux)
                diamond.close()
                p.drawPath(diamond, fill=1, stroke=1)
            if label:
                p.setFillColor(MUTED)
                p.setFont("Body", 8)
                p.drawString(*label_at, label)

        left, right = 236, CONTENT - 270
        box(0, 434, left, "EmailDirector", [], [
            "+makeWelcomeEmail(EmailBuilder): void",
            "+makeOrderConfirmationEmail(",
            "  EmailBuilder): void"])
        box(270, 416, right, "EmailBuilder", [], [
            "+setFrom(String): EmailBuilder",
            "+setTo(String): EmailBuilder",
            "+setSubject(String): EmailBuilder",
            "+setBody(String): EmailBuilder"], "<<interface>>")
        object_height = box(0, 230, left, "EmailObjectBuilder", ["-draft: EmailDraft {final}"], [
            "+setFrom(String): EmailObjectBuilder",
            "+setTo(String): EmailObjectBuilder",
            "+setSubject(String): EmailObjectBuilder",
            "+setBody(String): EmailObjectBuilder",
            "+getResult(): Email"])
        preview_height = box(270, 230, right, "EmailPreviewBuilder", ["-draft: EmailDraft {final}"], [
            "+setFrom(String): EmailPreviewBuilder",
            "+setTo(String): EmailPreviewBuilder",
            "+setSubject(String): EmailPreviewBuilder",
            "+setBody(String): EmailPreviewBuilder",
            "+getResult(): String"])
        email_height = box(0, 2, left, "Email", [
            "-from: String {final}", "-to: String {final}",
            "-subject: String {final}", "-body: String {final}"], [
            "~Email(EmailDraft)", "+getFrom(): String", "+getTo(): String",
            "+getSubject(): String", "+getBody(): String", "+toString(): String"],
            "<<final, immutable>>")
        draft_height = box(270, 37, right, "EmailDraft", [
            "~from: String", "~to: String", "~subject: String", "~body: String"],
            ["~validate(): void"], "<<final, package-private>>")
        connector([(236, 460), (270, 460)], label="uses", label_at=(238, 468))
        connector([(118, 230 + object_height), (118, 391), (345, 391), (345, 416)],
                  kind="realization")
        connector([(410, 230 + preview_height), (410, 416)], kind="realization")
        connector([(72, 230), (72, 2 + email_height)], label="creates", label_at=(80, 208))
        connector([(216, 230), (216, 201), (293, 201), (293, 37 + draft_height)],
                  kind="composition", label="owns 1", label_at=(240, 205))
        connector([(418, 230), (418, 37 + draft_height)], kind="composition",
                  label="owns 1", label_at=(424, 197))
        connector([(236, 105), (270, 105)])
        p.restoreState()
        self.y -= 540
        self.markdown.append("UML source: [uml.puml](uml.puml). The PDF embeds a vector class diagram.\n")

    def finish(self):
        self.pdf.save()
        (ROOT / "docs/report.md").write_text("\n".join(self.markdown), encoding="utf-8")
        print(f"Created {OUTPUT} ({self.page} pages)")


def build(github_url):
    register_fonts()
    r = Report(github_url)
    r.new_page("Builder Pattern: Email", "Java implementation and design report")
    r.paragraph("Student: Шалкар   |   Group: SE-2532   |   Submission: 12 September 2026, 16:00")
    r.heading("1. Introduction")
    r.paragraph("This project demonstrates the Builder design pattern using an email as the product. "
                "The same construction steps create two representations: an immutable Email object "
                "for use in Java code and a readable String preview. Email is one of the permitted "
                "products and differs from the supplied Custom PC example.")
    r.paragraph("The construction sequence is separated from the result representation. EmailDirector "
                "contains a welcome-email recipe and an order-confirmation recipe. It accepts only "
                "EmailBuilder, so each recipe can work with either concrete builder.")
    r.heading("2. Design and construction")
    r.table([
        ("Pattern role", "Implementation"),
        ("Immutable product", "Email: private final fields, no setters, package-private constructor."),
        ("Builder contract", "EmailBuilder: setFrom, setTo, setSubject and setBody."),
        ("Object representation", "EmailObjectBuilder.getResult() returns Email."),
        ("Text representation", "EmailPreviewBuilder.getResult() returns String."),
        ("Director", "EmailDirector: makeWelcomeEmail and makeOrderConfirmationEmail."),
        ("Internal state", "Each builder owns a separate EmailDraft with shared validation rules."),
        ("Client", "Main creates the builders, calls both recipes and prints both results."),
    ])
    r.paragraph("Both recipes use this order: sender, recipient, subject, body. Every step returns "
                "the same builder. getResult() belongs to each concrete builder because Email and "
                "String have different types; the director only needs the common construction steps.")
    r.paragraph("The application is a local console demonstration. It does not send email or require "
                "network access, a server, Maven, Gradle or external Java libraries.")

    r.new_page("3. UML class diagram")
    r.uml()
    r.paragraph("Legend: + public; - private; ~ package-private. Dashed lines with hollow triangles "
                "mean interface implementation; dashed arrows mean dependency; filled diamonds mean "
                "ownership. Each builder owns one draft. Email copies draft values during construction "
                "and does not retain the draft.", small=True)
    r.paragraph("Main is the client and is omitted to keep the pattern relationships readable. "
                "Private recipe constants, the preview template and private validation helpers are "
                "also omitted. The text result is Java's immutable String. Editable source: docs/uml.puml.", small=True)

    r.new_page("4. Clean Code principles", "All excerpts below are extracted from the submitted Java source files.")
    r.heading("1. Meaningful names and named constants")
    r.paragraph("Recipe values have names that explain their purpose. This avoids unexplained "
                "configuration literals in the construction steps and keeps changes in one place.")
    r.code(*excerpt("EmailDirector.java", "private static final String SUPPORT_ADDRESS", "private static final String WELCOME_SUBJECT"))
    r.heading("2. Single responsibility")
    r.paragraph("The preview builder formats text; the object builder creates Email; the director "
                "defines recipes. EmailDraft owns the common validation rules. Changing preview "
                "formatting therefore does not require changing the object product or the director.")
    r.code(*excerpt("EmailPreviewBuilder.java", "public String getResult()", "    }"))
    r.heading("3. Depend on an abstraction")
    r.paragraph("The director's parameter is EmailBuilder. It can apply the same recipe to either "
                "representation and never calls a concrete getResult(). A third implementation of "
                "the interface could reuse this recipe without editing the director.")
    r.code(*excerpt("EmailDirector.java", "public void makeWelcomeEmail", "    }"))

    r.new_page("4. Clean Code principles", "Shared rules, safe products and clear failures")
    r.heading("4. Do not repeat validation rules")
    r.paragraph("Both concrete getResult() methods call draft.validate(). A required-field or "
                "address rule is maintained in one helper instead of being duplicated and drifting "
                "between the object and text representations.")
    r.code(*excerpt("EmailDraft.java", "void validate()", "    }"))
    r.heading("5. Encapsulation and immutability")
    r.paragraph("Email is final, its state is private and final, and it exposes no setters. Its "
                "package-private constructor takes one internal draft and copies four immutable "
                "String values. The mutable draft itself is not stored in the product.")
    r.code(*excerpt("Email.java", "public final class Email", "    }"))
    r.heading("6. Clear errors at the result boundary")
    r.paragraph("A partially filled draft is allowed during construction, but getResult() rejects "
                "invalid state. The exception identifies the missing field, making the failure "
                "understandable to the caller.")
    r.code(*excerpt("EmailDraft.java", "private static void requireText", "    }"))

    r.new_page("5. Validation and conclusion")
    r.heading("7. Small methods and a fluent API")
    r.paragraph("Each construction step performs one assignment and returns this. Concrete return "
                "types preserve chaining while implementing the EmailBuilder interface.")
    r.code(*excerpt("EmailObjectBuilder.java", "public EmailObjectBuilder setSubject", "    }"))
    r.heading("Validation and executed checks")
    r.paragraph("All four fields are required and must contain non-whitespace text. Sender and "
                "recipient must match the documented simple email-address rule. Subjects must be "
                "single-line; message bodies may be multiline. Invalid state throws "
                "IllegalStateException from either getResult(). The address rule is intentionally "
                "limited and does not implement the full Internet email specification.")
    r.table([
        ("Check area", "Observed result"),
        ("Build and execution", "Compiled using JDK 24.0.1 with --release 17, -Xlint:all and -Werror. Main ran successfully."),
        ("Both recipes", "Object fields and complete preview text match each recipe."),
        ("Invalid input", "Both builders reject null/blank fields, malformed addresses and multiline subjects."),
        ("Fluent and reuse behavior", "Every step returns the same builder. Repeated steps replace values; existing results remain unchanged."),
        ("Test runner", "./test.sh completed: PASS: 64 behavioral checks."),
    ])
    r.paragraph("Builders retain their current draft and are intended for one thread. Both director "
                "recipes overwrite every field. Calling getResult() repeatedly does not append text "
                "or bypass validation. Editing a builder cannot change an earlier Email or String.")
    r.heading("Conclusion")
    r.paragraph("The implementation separates construction from representation using one fluent "
                "interface, two concrete builders and a director with two reusable recipes. The "
                "Email product is immutable, both builders validate their result, and the design "
                "avoids a long public constructor and repeated validation logic.")
    r.heading("GitHub and submission")
    if github_url:
        r.paragraph(github_url)
        r.pdf.linkURL(github_url, (MARGIN, r.y + 10, WIDTH - MARGIN, r.y + 25), relative=0)
        r.paragraph("The repository contains the Java source, README and staged publication commits. "
                    "The development-history.bundle file preserves the four original local development "
                    "commits and their exact history.", small=True)
    else:
        r.paragraph("GitHub publication is pending. The student's repository URL has not yet been "
                    "provided. Add the real repository link and publish the incremental local "
                    "commits before submitting this report to Moodle.", small=True)
    r.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-url", default="https://github.com/Shalkar111/builder-email-assignment")
    args = parser.parse_args()
    if args.github_url and not args.github_url.startswith("https://github.com/"):
        parser.error("--github-url must be a real HTTPS GitHub repository URL")
    build(args.github_url)
