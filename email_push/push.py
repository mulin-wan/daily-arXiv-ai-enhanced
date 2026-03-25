import json
import os
import sys
import argparse
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def format_paper_html(paper: dict, idx: int) -> str:
    title = paper.get("title", "Unknown Title")
    url = paper.get("abs", "")
    authors = paper.get("authors", [])
    author_str = ", ".join(authors[:3])
    if len(authors) > 3:
        author_str += " et al."

    categories = ", ".join(paper.get("categories", [])[:2])

    ai = paper.get("AI", {})
    tldr = ai.get("tldr", "N/A")
    motivation = ai.get("motivation", "")
    method = ai.get("method", "")
    result = ai.get("result", "")

    return f"""
    <div style="border-left:3px solid #1976D2;padding:10px 16px;margin:16px 0;background:#f8f9fa;border-radius:0 4px 4px 0;">
      <h3 style="margin:0 0 4px 0;font-size:15px;">
        [{idx}] <a href="{url}" style="color:#1565C0;text-decoration:none;">{title}</a>
      </h3>
      <p style="margin:2px 0;color:#666;font-size:13px;">
        {author_str} &nbsp;|&nbsp; <code style="background:#e8eaf6;padding:1px 5px;border-radius:3px;">{categories}</code>
      </p>
      <p style="margin:8px 0 4px 0;"><strong>TL;DR:</strong> {tldr}</p>
      <details style="margin-top:6px;">
        <summary style="cursor:pointer;color:#555;font-size:13px;">Show details</summary>
        <div style="margin-top:6px;font-size:13px;line-height:1.6;">
          <p><strong>Motivation:</strong> {motivation}</p>
          <p><strong>Method:</strong> {method}</p>
          <p><strong>Result:</strong> {result}</p>
        </div>
      </details>
    </div>
    """


def build_html(papers: list, digest_date: str) -> str:
    if papers:
        papers_html = "\n".join(
            format_paper_html(p, i + 1) for i, p in enumerate(papers)
        )
        summary = (
            f"<p style='color:#444;'>Found <strong>{len(papers)}</strong> papers "
            f"matching: <em>Railway &middot; AI &middot; Ontology</em></p>"
        )
    else:
        papers_html = "<p style='color:#888;'>No relevant papers found today.</p>"
        summary = ""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:24px;color:#333;">
  <h2 style="border-bottom:2px solid #1976D2;padding-bottom:8px;color:#0D47A1;">
    arXiv Daily Digest &mdash; {digest_date}
  </h2>
  <p style="color:#666;margin-top:4px;">Topics: Railway &middot; AI &middot; Ontology</p>
  {summary}
  {papers_html}
  <hr style="margin:32px 0;border:none;border-top:1px solid #ddd;">
  <p style="color:#aaa;font-size:11px;">Powered by daily-arXiv-ai-enhanced &bull; GitHub Actions</p>
</body>
</html>"""


def send_email(
    gmail_user: str,
    app_password: str,
    to_addr: str,
    subject: str,
    html_body: str,
):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_user, app_password)
        smtp.sendmail(gmail_user, to_addr, msg.as_string())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to AI-enhanced JSONL file")
    parser.add_argument("--date", default=str(date.today()), help="Date for header")
    args = parser.parse_args()

    gmail_user = os.environ.get("GMAIL_USER")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    email_to = os.environ.get("EMAIL_TO", gmail_user)

    if not gmail_user or not app_password:
        print(
            "Error: GMAIL_USER and GMAIL_APP_PASSWORD must be set", file=sys.stderr
        )
        sys.exit(1)

    papers = []
    if os.path.exists(args.data):
        with open(args.data) as f:
            for line in f:
                line = line.strip()
                if line:
                    papers.append(json.loads(line))

    subject = (
        f"[arXiv] {args.date} — {len(papers)} Railway/AI/Ontology paper(s)"
        if papers
        else f"[arXiv] {args.date} — No new papers today"
    )
    html_body = build_html(papers, args.date)

    send_email(gmail_user, app_password, email_to, subject, html_body)
    print(f"Email sent to {email_to}: {len(papers)} paper(s).", file=sys.stderr)


if __name__ == "__main__":
    main()
