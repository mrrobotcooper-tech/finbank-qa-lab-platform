export default {
  paths: ["automation/bdd/features/**/*.feature"],
  import: [
    "automation/bdd/support/world.ts",
    "automation/bdd/support/hooks.ts",
    "automation/bdd/steps/**/*.ts",
  ],
  format: ["progress", "junit:reports/cucumber-junit.xml"],
  parallel: 1,
};
