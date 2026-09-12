package assignment.builder;

import java.util.function.Consumer;
import java.util.function.Supplier;

/** Dependency-free behavioral checks; failures exit with an AssertionError. */
public final class BuilderChecks {
    private static final String VALID_FROM = "sender@example.com";
    private static final String VALID_TO = "reader@example.com";
    private static final String VALID_SUBJECT = "Meeting notes";
    private static final String VALID_BODY = "Hello!\nHere are the notes.";
    private static int checks;

    private BuilderChecks() {
    }

    public static void main(String[] args) {
        checkBothRecipes();
        checkFluentSteps(new EmailObjectBuilder());
        checkFluentSteps(new EmailPreviewBuilder());
        checkInvalidStates(EmailObjectBuilder::new,
                builder -> ((EmailObjectBuilder) builder).getResult());
        checkInvalidStates(EmailPreviewBuilder::new,
                builder -> ((EmailPreviewBuilder) builder).getResult());
        checkIndependentSnapshots();
        checkRepeatedStepsAndResults();
        System.out.println("PASS: " + checks + " behavioral checks.");
    }

    private static void checkBothRecipes() {
        EmailDirector director = new EmailDirector();
        checkRecipe(director::makeWelcomeEmail,
                "support@example.com", "Welcome to Study Shop",
                "Hello! Your account is ready. Thank you for joining Study Shop.");
        checkRecipe(director::makeOrderConfirmationEmail,
                "orders@example.com", "Your order is confirmed",
                "Hello! We received your order. We will email you when it ships.");
    }

    private static void checkRecipe(Consumer<EmailBuilder> recipe, String from,
                                    String subject, String body) {
        EmailObjectBuilder objectBuilder = new EmailObjectBuilder();
        EmailPreviewBuilder previewBuilder = new EmailPreviewBuilder();
        recipe.accept(objectBuilder);
        recipe.accept(previewBuilder);
        Email email = objectBuilder.getResult();
        check(email.getFrom().equals(from), "Recipe sender");
        check(email.getTo().equals("customer@example.com"), "Recipe recipient");
        check(email.getSubject().equals(subject), "Recipe subject");
        check(email.getBody().equals(body), "Recipe body");
        String expectedPreview = "=== Email Preview ===\nFrom: " + from
                + "\nTo: customer@example.com\nSubject: " + subject + "\n\n" + body + "\n";
        check(previewBuilder.getResult().equals(expectedPreview),
                "Same recipe produces the corresponding full text preview");
    }

    private static void checkFluentSteps(EmailBuilder builder) {
        check(builder.setFrom(VALID_FROM) == builder, "setFrom returns this");
        check(builder.setTo(VALID_TO) == builder, "setTo returns this");
        check(builder.setSubject(VALID_SUBJECT) == builder, "setSubject returns this");
        check(builder.setBody(VALID_BODY) == builder, "setBody returns this");
    }

    private static void checkInvalidStates(Supplier<EmailBuilder> factory,
                                           Consumer<EmailBuilder> finish) {
        expectInvalid(factory, finish, builder -> builder.setFrom(null), "From is required");
        expectInvalid(factory, finish, builder -> builder.setFrom("  "), "From is required");
        expectInvalid(factory, finish, builder -> builder.setTo(null), "To is required");
        expectInvalid(factory, finish, builder -> builder.setTo("\t"), "To is required");
        expectInvalid(factory, finish, builder -> builder.setSubject(null), "Subject is required");
        expectInvalid(factory, finish, builder -> builder.setSubject(" "), "Subject is required");
        expectInvalid(factory, finish, builder -> builder.setBody(null), "Body is required");
        expectInvalid(factory, finish, builder -> builder.setBody("\n"), "Body is required");
        expectInvalid(factory, finish, builder -> builder.setFrom("missing-at.example.com"),
                "From must be a valid email address");
        expectInvalid(factory, finish, builder -> builder.setTo("reader@example"),
                "To must be a valid email address");
        expectInvalid(factory, finish, builder -> builder.setTo("a@@example.com"),
                "To must be a valid email address");
        expectInvalid(factory, finish, builder -> builder.setFrom("a b@example.com"),
                "From must be a valid email address");
        expectInvalid(factory, finish, builder -> builder.setFrom("a@example.com\r\nExtra: x"),
                "From must be a valid email address");
        expectInvalid(factory, finish, builder -> builder.setSubject("Hello\nExtra: x"),
                "Subject must be a single line");
        expectInvalid(factory, finish, builder -> builder.setSubject("Hello\rExtra: x"),
                "Subject must be a single line");
    }

    private static void expectInvalid(Supplier<EmailBuilder> factory,
                                       Consumer<EmailBuilder> finish,
                                       Consumer<EmailBuilder> change, String message) {
        EmailBuilder builder = factory.get();
        configureValidEmail(builder);
        change.accept(builder); // Invalid drafts are allowed until getResult().
        try {
            finish.accept(builder);
            throw new AssertionError("Expected validation failure: " + message);
        } catch (IllegalStateException exception) {
            check(message.equals(exception.getMessage()), "Clear error: " + message);
        }
    }

    private static void checkIndependentSnapshots() {
        EmailObjectBuilder builder = new EmailObjectBuilder();
        configureValidEmail(builder);
        Email original = builder.getResult();
        EmailDirector director = new EmailDirector();
        director.makeOrderConfirmationEmail(builder);
        Email changed = builder.getResult();
        check(original.getFrom().equals(VALID_FROM), "Original sender is unchanged");
        check(original.getTo().equals(VALID_TO), "Original recipient is unchanged");
        check(original.getSubject().equals(VALID_SUBJECT), "Original subject is unchanged");
        check(original.getBody().equals(VALID_BODY), "Original body is unchanged");
        check(changed.getFrom().equals("orders@example.com"), "Reused builder uses new sender");
        check(changed.getSubject().equals("Your order is confirmed"), "Reused builder uses new subject");
        check(original != changed, "Each result is a separate object");
    }

    private static void checkRepeatedStepsAndResults() {
        EmailPreviewBuilder builder = new EmailPreviewBuilder();
        configureValidEmail(builder);
        String original = builder.getResult();
        check(original.equals(builder.getResult()), "Repeated results do not append text");
        builder.setSubject("Updated subject");
        String updated = builder.getResult();
        check(updated.contains("Subject: Updated subject\n"), "Repeated step replaces value");
        check(!updated.contains(VALID_SUBJECT), "Old subject is absent from new preview");
        check(original.contains(VALID_SUBJECT), "Existing String result is unchanged");
        check(updated.endsWith(VALID_BODY + "\n"), "Multiline body is preserved");

        EmailDirector director = new EmailDirector();
        director.makeWelcomeEmail(builder);
        director.makeOrderConfirmationEmail(builder);
        String orderPreview = builder.getResult();
        check(orderPreview.contains("From: orders@example.com\n"), "Preview can switch recipes");
        check(!orderPreview.contains("Welcome to Study Shop"), "No stale welcome content");

        builder.setTo(null);
        try {
            builder.getResult();
            throw new AssertionError("A previous result must not bypass validation");
        } catch (IllegalStateException exception) {
            check(exception.getMessage().equals("To is required"), "Revalidates after every edit");
        }
        builder.setTo(VALID_TO);
        check(builder.getResult().contains("To: " + VALID_TO), "Invalid draft can be repaired");
    }

    private static void configureValidEmail(EmailBuilder builder) {
        builder.setFrom(VALID_FROM).setTo(VALID_TO)
                .setSubject(VALID_SUBJECT).setBody(VALID_BODY);
    }

    private static void check(boolean condition, String description) {
        if (!condition) {
            throw new AssertionError(description);
        }
        checks++;
    }
}
