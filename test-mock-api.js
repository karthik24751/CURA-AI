// Simple test to verify mock API works
const mockAPI = {
  trials: {
    search: async (params) => ({
      data: {
        trials: [
          {
            nct_id: "NCT05123456",
            title: "Novel Immunotherapy for Advanced Cancer Treatment",
            summary: "A Phase II clinical trial evaluating the safety and efficacy of a new immunotherapy approach for patients with advanced solid tumors.",
            phase: "Phase 2",
            status: "Recruiting",
            match_score: 92
          }
        ],
        count: 1
      }
    })
  }
};

// Test the mock API
async function testMockAPI() {
  try {
    const result = await mockAPI.trials.search({ condition: 'cancer' });
    console.log('Mock API working:', result);
    console.log('Trials count:', result.data.trials.length);
  } catch (error) {
    console.error('Mock API error:', error);
  }
}

testMockAPI();
