package assignment.builder;

/** Builds a readable text representation, without constructing an Email object. */
public final class EmailPreviewBuilder implements EmailBuilder {
    private static final String PREVIEW_TEMPLATE = """
            === Email Preview ===
            From: %s
            To: %s
            Subject: %s

            %s
            """;

    private final EmailDraft draft = new EmailDraft();

    @Override
    public EmailPreviewBuilder setFrom(String from) {
        draft.from = from;
        return this;
    }

    @Override
    public EmailPreviewBuilder setTo(String to) {
        draft.to = to;
        return this;
    }

    @Override
    public EmailPreviewBuilder setSubject(String subject) {
        draft.subject = subject;
        return this;
    }

    @Override
    public EmailPreviewBuilder setBody(String body) {
        draft.body = body;
        return this;
    }

    public String getResult() {
        draft.validate();
        return PREVIEW_TEMPLATE.formatted(
                draft.from, draft.to, draft.subject, draft.body);
    }
}
