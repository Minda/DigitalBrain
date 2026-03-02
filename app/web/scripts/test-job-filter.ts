#!/usr/bin/env tsx

/**
 * Test script to validate AI job filtering logic
 *
 * Usage: ANTHROPIC_API_KEY=sk-ant-... npx tsx scripts/test-job-filter.ts
 */

import { isJobRelevant } from "@/modules/jobs/filters/ai-filter";

// Sample jobs to test filtering
const testJobs = [
  {
    company: "Office Solutions Inc",
    title: "Office Manager",
    description: "We're looking for an experienced Office Manager to manage our day-to-day operations, coordinate meetings, handle facilities management, and support our executive team.",
  },
  {
    company: "Sales Corp",
    title: "Senior Sales Representative",
    description: "Join our sales team! We're looking for a driven sales professional to drive revenue growth, manage client relationships, and close deals.",
  },
  {
    company: "OpenAI",
    title: "AI Safety Research Engineer",
    description: "Join our safety team to work on alignment research, interpretability, and building systems for monitoring AI behavior. Strong Python and PyTorch skills required.",
  },
  {
    company: "Anthropic",
    title: "ML Engineer - AI Safety",
    description: "Help us build safe, steerable AI systems. Work on RLHF, constitutional AI, and interpretability research. Experience with transformers and large-scale training required.",
  },
  {
    company: "Google DeepMind",
    title: "Software Engineer",
    description: "Build infrastructure for training frontier AI models. Work with CUDA, distributed systems, and GPU optimization. Previous experience with ML systems helpful but not required.",
  },
  {
    company: "Marketing Agency",
    title: "Marketing Manager",
    description: "Lead our marketing campaigns, manage social media, create content strategies, and drive brand awareness.",
  },
  {
    company: "Crypto Startup",
    title: "Senior AI Engineer - Web3",
    description: "Build AI-powered trading bots for cryptocurrency markets. Work with blockchain, smart contracts, and machine learning.",
  },
  {
    company: "AI Startup",
    title: "Junior ML Engineer",
    description: "Entry-level role building ML models for our product. 0-2 years experience. Learn from our senior team.",
  },
  {
    company: "Scale AI",
    title: "AI Observability Engineer",
    description: "Build monitoring and observability tools for LLM systems. Work on eval frameworks, debugging tools, and production monitoring. Python, TypeScript, and ML experience required.",
  },
  {
    company: "Random Corp",
    title: "Frontend Developer",
    description: "Build React UIs for our e-commerce platform. No AI/ML component. Focus on pixel-perfect designs and responsive layouts.",
  },
];

async function main() {
  console.log("🔍 Testing AI Job Filter\n");
  console.log("=" .repeat(80));

  let relevant = 0;
  let filtered = 0;

  for (const job of testJobs) {
    console.log(`\n📋 Testing: ${job.company} - ${job.title}`);
    console.log(`Description: ${job.description.substring(0, 80)}...`);

    try {
      const result = await isJobRelevant(
        job.description,
        job.title,
        job.company
      );

      const emoji = result.isRelevant ? "✅" : "❌";
      console.log(
        `${emoji} Result: ${result.isRelevant ? "RELEVANT" : "FILTERED OUT"}`
      );
      console.log(`   Reason: ${result.reason}`);
      console.log(`   Confidence: ${result.confidence}`);

      if (result.isRelevant) {
        relevant++;
      } else {
        filtered++;
      }
    } catch (error) {
      console.error(`❌ Error filtering job:`, error);
    }

    console.log("-".repeat(80));
  }

  console.log("\n" + "=".repeat(80));
  console.log(`\n📊 Summary:`);
  console.log(`   Total jobs tested: ${testJobs.length}`);
  console.log(`   ✅ Relevant: ${relevant}`);
  console.log(`   ❌ Filtered out: ${filtered}`);
  console.log(`   Filter rate: ${((filtered / testJobs.length) * 100).toFixed(1)}%`);

  console.log("\n✨ Expected results:");
  console.log("   - Office Manager: FILTERED");
  console.log("   - Sales Rep: FILTERED");
  console.log("   - OpenAI Safety Engineer: RELEVANT");
  console.log("   - Anthropic ML Engineer: RELEVANT");
  console.log("   - Google DeepMind SWE: RELEVANT");
  console.log("   - Marketing Manager: FILTERED");
  console.log("   - Crypto AI Engineer: FILTERED (dealbreaker: crypto)");
  console.log("   - Junior ML Engineer: FILTERED (dealbreaker: junior)");
  console.log("   - Scale AI Observability: RELEVANT");
  console.log("   - Frontend Developer: FILTERED (no AI component)");
}

main()
  .then(() => {
    console.log("\n✅ Test complete!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Test failed:", error);
    process.exit(1);
  });
