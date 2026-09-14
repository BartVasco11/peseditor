// @ts-check
import { module } from "@prisma/composer";
import aiChatbotService from "./service.mjs";

export default module("peseditor", ({ provision }) => {
  provision(aiChatbotService, { id: "aichatbot" });
});
