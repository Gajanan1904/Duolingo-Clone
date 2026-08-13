// E2E test script simulating browser session against Next.js proxy on http://localhost:3000

async function runE2ETest() {
  console.log("=== STARTING LINGUAQUEST END-TO-END INTEGRATION TEST ===");
  
  let cookieJar = "";

  function extractCookies(response) {
    const rawCookies = response.headers.getSetCookie 
      ? response.headers.getSetCookie() 
      : [response.headers.get("set-cookie")].filter(Boolean);
    
    if (rawCookies && rawCookies.length > 0) {
      for (const cookie of rawCookies) {
        if (!cookie) continue;
        const [cookiePart] = cookie.split(";");
        const [name, val] = cookiePart.split("=");
        const cookies = Object.fromEntries(
          cookieJar.split("; ").filter(Boolean).map(c => c.split("="))
        );
        cookies[name.trim()] = val ? val.trim() : "";
        cookieJar = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join("; ");
      }
    }
  }

  function getCookie(name) {
    const parts = cookieJar.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    if (cookieJar.startsWith(`${name}=`)) return cookieJar.split(";")[0].split("=")[1];
    return null;
  }

  async function apiRequest(url, method = "GET", body = null) {
    const headers = {
      "Content-Type": "application/json",
    };
    if (cookieJar) {
      headers["Cookie"] = cookieJar;
    }
    if (method !== "GET") {
      const csrfToken = getCookie("csrftoken");
      if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
      }
    }

    const response = await fetch(`http://localhost:3000${url}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    extractCookies(response);

    const status = response.status;
    let data;
    try {
      data = await response.json();
    } catch {
      data = null;
    }

    return { status, data, headers: response.headers };
  }

  // 1. Session Bootstrap
  console.log("\n[1] Testing GET /api/auth/session/ (Demo Session Bootstrap)...");
  const sessionRes = await apiRequest("/api/auth/session/");
  console.log(`Status: ${sessionRes.status}, Authenticated: ${sessionRes.data?.authenticated}, User: ${sessionRes.data?.user?.username}`);
  console.log(`Cookies established: ${cookieJar}`);
  if (sessionRes.status !== 200 || !sessionRes.data?.authenticated) {
    throw new Error("Failed to bootstrap session!");
  }

  // 2. Learning Path
  console.log("\n[2] Testing GET /api/path/ through proxy...");
  const pathRes = await apiRequest("/api/path/");
  console.log(`Status: ${pathRes.status}, Course: ${pathRes.data?.course?.name}, Units: ${pathRes.data?.units?.length}`);
  if (pathRes.status !== 200 || !pathRes.data?.course) {
    throw new Error("Failed GET /api/path/");
  }

  // 3. User Stats
  console.log("\n[3] Testing GET /api/stats/ through proxy...");
  const statsRes = await apiRequest("/api/stats/");
  console.log(`Status: ${statsRes.status}, Total XP: ${statsRes.data?.total_xp}, Hearts: ${statsRes.data?.hearts}/${statsRes.data?.max_hearts}, Streak: ${statsRes.data?.current_streak}`);
  if (statsRes.status !== 200) {
    throw new Error("Failed GET /api/stats/");
  }

  // 4. Fetch Lesson 1 Detail
  console.log("\n[4] Testing GET /api/lessons/1/ through proxy...");
  const lessonRes = await apiRequest("/api/lessons/1/");
  console.log(`Status: ${lessonRes.status}, Lesson Title: "${lessonRes.data?.title}", Total Exercises: ${lessonRes.data?.exercises?.length}`);
  if (lessonRes.status !== 200 || !lessonRes.data?.exercises) {
    throw new Error("Failed GET /api/lessons/1/");
  }

  const exercises = lessonRes.data.exercises;
  let attemptId = null;

  // 5. Test Multiple Choice Exercise (Exercise 1)
  console.log(`\n[5] Testing Exercise 1: Multiple Choice (${exercises[0].type})...`);
  console.log(`Question: "${exercises[0].question}"`);
  const mcRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[0].id,
    answer: { value: "Hello" }
  });
  console.log(`Status: ${mcRes.status}, Correct: ${mcRes.data?.correct}, Attempt ID: ${mcRes.data?.attempt_id}, Hearts: ${mcRes.data?.hearts?.current}`);
  attemptId = mcRes.data?.attempt_id;
  if (mcRes.status !== 200 || !mcRes.data?.correct || !attemptId) {
    throw new Error("Failed Exercise 1 (Multiple Choice)");
  }

  // 6. Test Heart Deduction on Incorrect Answer
  console.log(`\n[6] Testing Heart Deduction on Incorrect Answer (Exercise 2)...`);
  const initialHearts = mcRes.data.hearts.current;
  const wrongRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[1].id,
    answer: { value: "WrongAnswer" }
  });
  console.log(`Status: ${wrongRes.status}, Correct: ${wrongRes.data?.correct}, Hearts before: ${initialHearts}, Hearts after: ${wrongRes.data?.hearts?.current}`);
  if (wrongRes.status !== 200 || wrongRes.data?.correct !== false || wrongRes.data?.hearts?.current !== initialHearts - 1) {
    throw new Error("Heart deduction failed!");
  }

  // 7. Test Translate Exercise (Exercise 2 - Correct)
  console.log(`\n[7] Testing Exercise 2: Translate (${exercises[1].type})...`);
  const transRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[1].id,
    answer: { value: "Hola" }
  });
  console.log(`Status: ${transRes.status}, Correct: ${transRes.data?.correct}`);
  if (transRes.status !== 200 || !transRes.data?.correct) {
    throw new Error("Failed Exercise 2 (Translate)");
  }

  // 8. Test Word Bank Exercise (Exercise 3)
  console.log(`\n[8] Testing Exercise 3: Word Bank (${exercises[2].type})...`);
  const wbRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[2].id,
    answer: { words: ["Yo", "como", "una", "manzana"] }
  });
  console.log(`Status: ${wbRes.status}, Correct: ${wbRes.data?.correct}`);
  if (wbRes.status !== 200 || !wbRes.data?.correct) {
    throw new Error("Failed Exercise 3 (Word Bank)");
  }

  // 9. Test Match Pairs Exercise (Exercise 4)
  console.log(`\n[9] Testing Exercise 4: Match Pairs (${exercises[3].type})...`);
  const mpRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[3].id,
    answer: { pairs: { "1": "Hola", "2": "Adiós" } }
  });
  console.log(`Status: ${mpRes.status}, Correct: ${mpRes.data?.correct}`);
  if (mpRes.status !== 200 || !mpRes.data?.correct) {
    throw new Error("Failed Exercise 4 (Match Pairs)");
  }

  // 10. Test Fill in the Blank Exercise (Exercise 5)
  console.log(`\n[10] Testing Exercise 5: Fill in Blank (${exercises[4].type})...`);
  const fbRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[4].id,
    answer: { value: "como" }
  });
  console.log(`Status: ${fbRes.status}, Correct: ${fbRes.data?.correct}`);
  if (fbRes.status !== 200 || !fbRes.data?.correct) {
    throw new Error("Failed Exercise 5 (Fill in Blank)");
  }

  // 11. Test Type Answer Exercise (Exercise 6)
  console.log(`\n[11] Testing Exercise 6: Type Answer (${exercises[5].type})...`);
  const taRes = await apiRequest("/api/lessons/1/answer/", "POST", {
    exercise_id: exercises[5].id,
    answer: { value: "Gracias" }
  });
  console.log(`Status: ${taRes.status}, Correct: ${taRes.data?.correct}`);
  if (taRes.status !== 200 || !taRes.data?.correct) {
    throw new Error("Failed Exercise 6 (Type Answer)");
  }

  // 12. Complete Lesson
  console.log(`\n[12] Testing POST /api/lessons/1/complete/ with attempt_id=${attemptId}...`);
  const compRes = await apiRequest("/api/lessons/1/complete/", "POST", {
    attempt_id: attemptId
  });
  console.log(`Status: ${compRes.status}, Success: ${compRes.data?.success}, XP Earned: ${compRes.data?.rewards?.xp_earned}, Total XP: ${compRes.data?.stats?.total_xp}, Skill Crowns: ${compRes.data?.skill?.crowns}`);
  if (compRes.status !== 200 || !compRes.data?.success) {
    throw new Error("Failed to complete lesson!");
  }

  // 13. Profile
  console.log("\n[13] Testing GET /api/profile/ through proxy...");
  const profRes = await apiRequest("/api/profile/");
  console.log(`Status: ${profRes.status}, User: ${profRes.data?.user?.username}, Lessons Completed: ${profRes.data?.progress?.lessons_completed}, Total XP: ${profRes.data?.stats?.total_xp}`);
  if (profRes.status !== 200 || !profRes.data?.user) {
    throw new Error("Failed GET /api/profile/");
  }

  // 14. Leaderboard
  console.log("\n[14] Testing GET /api/leaderboard/ through proxy...");
  const lbRes = await apiRequest("/api/leaderboard/");
  console.log(`Status: ${lbRes.status}, Total Entries: ${lbRes.data?.leaderboard?.length}, Current User Rank: #${lbRes.data?.current_user_rank}`);
  if (lbRes.status !== 200 || !lbRes.data?.leaderboard) {
    throw new Error("Failed GET /api/leaderboard/");
  }

  // 15. Heart Refill
  console.log("\n[15] Testing POST /api/practice/hearts/ (Refill Hearts)...");
  const refillRes = await apiRequest("/api/practice/hearts/", "POST", {});
  console.log(`Status: ${refillRes.status}, Success: ${refillRes.data?.success}, Hearts Refilled: ${refillRes.data?.hearts?.current}/${refillRes.data?.hearts?.max}`);
  if (refillRes.status !== 200 || !refillRes.data?.success || refillRes.data?.hearts?.current !== refillRes.data?.hearts?.max) {
    throw new Error("Failed POST /api/practice/hearts/");
  }

  console.log("\n=======================================================");
  console.log(">>> ALL 15 END-TO-END INTEGRATION TESTS PASSED! <<<");
  console.log("=======================================================\n");
}

runE2ETest().catch((err) => {
  console.error("\nTEST FAILED:", err);
  process.exit(1);
});
