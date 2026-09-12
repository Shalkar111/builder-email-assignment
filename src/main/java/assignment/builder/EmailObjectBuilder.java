package assignment.builder;

/** Builds the Email object representation. */
public final class EmailObjectBuilder implements EmailBuilder {
    private final EmailDraft draft = new EmailDraft();

    @Override
    public EmailObjectBuilder setFrom(String from) {
        draft.from = from;
        return this;
    }

    @Override
    public EmailObjectBuilder setTo(String to) {
        draft.to = to;
        return this;
    }

    @Override
    public EmailObjectBuilder setSubject(String subject) {
        draft.subject = subject;
        return this;
    }

    @Override
    public EmailObjectBuilder setBody(String body) {
        draft.body = body;
        return this;
    }

    public Email getResult() {
        draft.validate();
        return new Email(draft);
    }
}
