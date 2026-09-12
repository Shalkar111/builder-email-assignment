package assignment.builder;

import java.util.regex.Pattern;

/** Package-private mutable state shared by the two builder implementations. */
final class EmailDraft {
    // A deliberately simple classroom check, not full Internet email validation.
    private static final Pattern ADDRESS_PATTERN =
            Pattern.compile("[^\\s@]+@[^\\s@]+\\.[^\\s@]+");

    String from;
    String to;
    String subject;
    String body;

    void validate() {
        requireAddress(from, "From");
        requireAddress(to, "To");
        requireText(subject, "Subject");
        requireSingleLine(subject, "Subject");
        requireText(body, "Body");
    }

    private static void requireAddress(String value, String field) {
        requireText(value, field);
        if (!ADDRESS_PATTERN.matcher(value).matches()) {
            throw new IllegalStateException(field + " must be a valid email address");
        }
    }

    private static void requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalStateException(field + " is required");
        }
    }

    private static void requireSingleLine(String value, String field) {
        if (value.contains("\n") || value.contains("\r")) {
            throw new IllegalStateException(field + " must be a single line");
        }
    }
}
