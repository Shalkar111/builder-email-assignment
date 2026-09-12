package assignment.builder;

/** Reusable recipes. The director knows only the EmailBuilder interface. */
public final class EmailDirector {
    private static final String SUPPORT_ADDRESS = "support@example.com";
    private static final String ORDERS_ADDRESS = "orders@example.com";
    private static final String CUSTOMER_ADDRESS = "customer@example.com";
    private static final String WELCOME_SUBJECT = "Welcome to Study Shop";
    private static final String WELCOME_BODY =
            "Hello! Your account is ready. Thank you for joining Study Shop.";
    private static final String ORDER_SUBJECT = "Your order is confirmed";
    private static final String ORDER_BODY =
            "Hello! We received your order. We will email you when it ships.";

    public void makeWelcomeEmail(EmailBuilder builder) {
        builder.setFrom(SUPPORT_ADDRESS)
                .setTo(CUSTOMER_ADDRESS)
                .setSubject(WELCOME_SUBJECT)
                .setBody(WELCOME_BODY);
    }

    public void makeOrderConfirmationEmail(EmailBuilder builder) {
        builder.setFrom(ORDERS_ADDRESS)
                .setTo(CUSTOMER_ADDRESS)
                .setSubject(ORDER_SUBJECT)
                .setBody(ORDER_BODY);
    }
}
