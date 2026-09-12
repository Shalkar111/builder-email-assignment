package assignment.builder;

/** Console demonstration only: it does not send email or connect to a network. */
public final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        EmailDirector director = new EmailDirector();
        EmailObjectBuilder objectBuilder = new EmailObjectBuilder();
        EmailPreviewBuilder previewBuilder = new EmailPreviewBuilder();

        director.makeWelcomeEmail(objectBuilder);
        director.makeWelcomeEmail(previewBuilder);
        printResults("WELCOME EMAIL", objectBuilder, previewBuilder);

        director.makeOrderConfirmationEmail(objectBuilder);
        director.makeOrderConfirmationEmail(previewBuilder);
        printResults("ORDER CONFIRMATION", objectBuilder, previewBuilder);

        demonstrateValidation();
    }

    private static void printResults(String title, EmailObjectBuilder objectBuilder,
                                     EmailPreviewBuilder previewBuilder) {
        Email email = objectBuilder.getResult();
        String preview = previewBuilder.getResult();

        System.out.println("--- " + title + " ---");
        System.out.println("Object: " + email);
        System.out.println(preview);
    }

    private static void demonstrateValidation() {
        try {
            new EmailObjectBuilder().getResult();
        } catch (IllegalStateException exception) {
            System.out.println("Expected validation error: " + exception.getMessage());
        }
    }
}
