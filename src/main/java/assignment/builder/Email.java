package assignment.builder;

/** Immutable snapshot: later changes to a builder cannot change this email. */
public final class Email {
    private final String from;
    private final String to;
    private final String subject;
    private final String body;

    Email(EmailDraft draft) {
        this.from = draft.from;
        this.to = draft.to;
        this.subject = draft.subject;
        this.body = draft.body;
    }

    public String getFrom() {
        return from;
    }

    public String getTo() {
        return to;
    }

    public String getSubject() {
        return subject;
    }

    public String getBody() {
        return body;
    }

    @Override
    public String toString() {
        return "Email[from=" + from + ", to=" + to
                + ", subject=" + subject + ", body=" + body + "]";
    }
}
