package assignment.builder;

/** Shared construction steps. Each concrete builder defines its own result type. */
public interface EmailBuilder {
    EmailBuilder setFrom(String from);

    EmailBuilder setTo(String to);

    EmailBuilder setSubject(String subject);

    EmailBuilder setBody(String body);
}
