import { clerkMiddleware } from "@clerk/nextjs/server";

export default clerkMiddleware();

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jte?|ttf|woff2?|ico|gif|svg|png|jpg|jpeg|webp)).*)",
    "/(api|trpc)(.*)",
  ],
};
