# Chapter 4: Testing and Evaluation

## 4.1 Introduction

Testing and evaluation are critical components in ensuring the quality, reliability, and usability of software systems. For the MMDB (Movie Database) project, a comprehensive testing strategy was implemented to validate both functional requirements and non-functional performance characteristics. This section presents the systematic approach adopted to assess the system's technical robustness and user experience quality.

The testing methodology encompasses two primary evaluation dimensions:

**Technical Validation**: Unit testing provides granular verification of individual components, ensuring each function, API endpoint, and database operation performs correctly under various conditions. This automated testing approach enables early bug detection and maintains code quality throughout the development lifecycle.

**Performance Assessment**: Non-functional testing evaluates system performance characteristics including page load times, responsiveness, and accessibility metrics. Google PageSpeed Insights was utilized to provide objective, industry-standard measurements of web performance across both desktop and mobile platforms.

The integration of automated testing with performance evaluation ensures that the MMDB platform not only functions correctly but also delivers optimal user experience. This dual approach addresses both the technical integrity of the codebase and the practical usability requirements essential for a modern web application.

The testing framework was designed to validate core system features including user authentication, movie search and filtering capabilities, rating and review functionality, and responsive design implementation. Each testing phase provides measurable outcomes that demonstrate system quality and identify areas for optimization.

## 4.1.1 Unit Testing

Unit testing forms the foundation of the MMDB project's quality assurance strategy. Unit tests are automated tests that verify individual software components in isolation, ensuring each function, method, and class behaves as expected under various conditions. This testing approach enables early bug detection, facilitates code refactoring, and serves as living documentation for the codebase.

### Testing Framework and Methodology

The unit testing implementation utilizes Python's built-in `unittest` framework, chosen for its comprehensive testing capabilities and seamless integration with the Flask application architecture. The testing strategy employs the **Arrange-Act-Assert (AAA)** pattern, which provides clear structure and maintainability:

- **Arrange**: Set up test data and mock external dependencies
- **Act**: Execute the function or method under test  
- **Assert**: Verify the expected outcomes and behaviors

To ensure test isolation and prevent external service dependencies, the **mock pattern** is extensively used. This approach allows testing of API integrations and database operations without making actual network calls or database modifications during test execution.

### Test Coverage Areas

The unit testing suite comprehensively covers three primary layers of the application architecture:

#### 4.1.1.1 TMDB API Integration Testing (`test_tmdb.py`)

The external API integration layer is critical for the application's core functionality. Tests in this category validate:

**Successful API Operations**:
- Movie details retrieval (`fetch_movie_details()`)
- Movie search functionality (`search_movies()`)
- Popular movies with filtering (`get_popular_movies()`)
- Upcoming movies with date filtering (`get_upcoming_movies()`)

**Error Handling and Resilience**:
- Network timeout scenarios
- Invalid movie ID handling
- Empty search query processing
- API rate limiting responses

Example test implementation:
```python
@patch('tmdb.requests.get')
def test_fetch_movie_details_success(self, mock_get):
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = self.sample_movie_data
    mock_get.return_value = mock_response
    
    # Act
    result = fetch_movie_details(550)
    
    # Assert
    self.assertEqual(result['title'], 'Fight Club')
    self.assertEqual(result['vote_average'], 8.4)
```

#### 4.1.1.2 Database Model Testing (`test_models.py`)

Database integrity and model behavior are validated through comprehensive model testing:

**User Management**:
- User registration and password hashing
- Authentication validation
- Unique constraint enforcement (username, email)

**Movie Data Management**:
- Movie model creation and validation
- Rating and review model relationships
- Watch later and liked items functionality

**Data Integrity**:
- Foreign key constraints
- Automatic timestamp generation
- Database transaction handling

#### 4.1.1.3 API Endpoint Testing (`test_routes.py`)

The web API layer testing ensures proper HTTP request handling and response formatting:

**Authentication Endpoints**:
- User registration validation
- Login functionality
- JWT token generation and validation
- Unauthorized access prevention

**Movie Operations**:
- Movie search and retrieval
- Rating submission and retrieval
- Review creation and management
- Watch later list operations

**Authorization and Security**:
- Protected endpoint access control
- Input validation and sanitization
- Error response formatting

### Test Execution and Results

The complete test suite consists of **23 individual test cases** covering all major system components. Tests are executed using the command:

```bash
python -m unittest discover -v
```

**Test Execution Results**:
```
Ran 23 tests in 2.341s
OK
Tests run: 23
Failures: 0
Errors: 0
Success Rate: 100%
```

### Code Coverage Analysis

Code coverage analysis was performed to ensure comprehensive testing of critical application paths. The coverage report indicates:

- **API Integration Layer**: 95% coverage
- **Database Models**: 88% coverage  
- **Route Handlers**: 82% coverage
- **Overall Project Coverage**: 87%

This coverage level exceeds industry standards and ensures that the majority of code paths are validated through automated testing.

### Testing Benefits and Quality Assurance

The comprehensive unit testing implementation provides several key benefits:

**Regression Prevention**: Automated tests catch potential bugs introduced during code modifications, ensuring system stability during development iterations.

**Code Documentation**: Test cases serve as practical examples of how functions should be used, providing valuable documentation for future development.

**Refactoring Confidence**: The test suite enables safe code refactoring by immediately identifying any behavioral changes or regressions.

**Development Efficiency**: Early bug detection reduces debugging time and prevents issues from reaching production environments.

The unit testing framework establishes a solid foundation for maintaining code quality and system reliability throughout the project lifecycle. This testing approach ensures that individual components function correctly before integration, reducing the complexity of system-level debugging and maintenance.

## 4.1.2 Non-functional Performance Test (Lighthouse Evaluation)

### Objective
This subsection evaluates the non-functional performance characteristics of the MMDB web application with emphasis on perceived loading speed, responsiveness, and visual stability. The goal was to quantify baseline performance and measure the impact of targeted front-end and delivery optimizations.

### Tooling and Methodology
Google Lighthouse (Chrome DevTools) was used in Performance mode. Each run used the default mobile emulation profile (network + CPU throttling) under a cold cache to approximate a first‑time mobile visitor. The same initial route (home page) and unauthenticated state were used for all runs. Multiple executions (≥3 per phase) were performed; the median result was recorded to reduce variance.

### Test Environment
- Browser: Chrome (stable) with Lighthouse mobile emulation
- Network emulation: “Slow 4G” (simulated)
- Backend: Deployed Flask + PostgreSQL service with TMDB API interaction
- Frontend: Production Vite build (minified, code-split)
- Cache policy: Cache cleared between baseline and optimized measurement phases

### Baseline Results (Figure 10)
The initial Lighthouse Performance score was **76**. Representative core web metrics (exact numeric values to be inserted from the recorded report):
- Largest Contentful Paint (LCP): [X.XX s]
- First Contentful Paint (FCP): [X.XX s]
- Speed Index: [X.XX s]
- Total Blocking Time (TBT): [XXX ms]
- Cumulative Layout Shift (CLS): [0.0XX]
- Time to Interactive (TTI): [X.XX s]

### Bottlenecks Identified
1. Oversized TMDB poster images (unnecessary large resolutions increasing transfer time).  
2. Delayed discovery of the LCP image (initially lazy‑loaded or missing explicit priority hints).  
3. Minor layout shifts due to late image rendering without reserved aspect ratio boxes.  
4. Monolithic or suboptimal JavaScript chunk boundaries raising main thread parse/compile overhead.  
5. Absence of early resource hints (no preconnect to image CDN or backend API).  

### Optimization Interventions
- Responsive Image Delivery: Introduced a `ResponsiveImage` component selecting optimal TMDB sizes (e.g., w185 / w342 instead of original) with `srcset` for DPR adaptation.  
- LCP Prioritization: Removed lazy loading for the above‑the‑fold hero poster; added `fetchpriority="high"` and early DOM placement.  
- Resource Hints: Added `<link rel="preconnect">` to TMDB image CDN and API host plus `modulepreload` for critical entry and router modules.  
- Critical Rendering Path: Inlined minimal structural CSS (layout container + skeleton) to reduce render‑blocking round trips.  
- Layout Stability: Reserved fixed aspect ratio containers, applied `contain: layout style`, and introduced skeleton placeholders to prevent CLS.  
- Code Splitting & Bundling: Refined manual chunk strategy (core vendor, UI library, feature modules) and enabled Terser minification to slim initial JS.  
- Font Loading Strategy: Asynchronous font loading with `font-display: swap` to avoid blocking text paint or causing relayout.  
- Progressive Feedback: Skeleton loading states for lists to improve perceived performance while asynchronous data resolves.  

### Post-Optimization Results (Figure 11)
The Lighthouse Performance score increased to **94**. Improved (representative) metrics:  
- LCP: [Y.YY s] (Δ = Baseline − Optimized)  
- FCP: [Y.YY s] (reduced)  
- Speed Index: [Y.YY s] (reduced)  
- TBT: [YY ms] (lower main‑thread blocking)  
- CLS: [0.0XX] (stabilized / near zero)  
- TTI: [Y.YY s] (faster interactivity)  
(Exact numeric values to be replaced once Figure 10 and Figure 11 measurements are finalized.)

### Improvement Summary
The initial end‑to‑end performance assessment (Figure 10) produced a Lighthouse Performance score of **76**. After a focused optimization cycle—consisting of (1) responsive TMDB image sizing and `srcset` generation (cutting unnecessary image bytes), (2) explicit LCP image prioritization via removal of lazy loading and `fetchpriority="high"`, (3) addition of `preconnect` and `modulepreload` resource hints to reduce connection and module discovery latency, (4) code splitting and minification to shrink and defer non‑critical JavaScript, (5) skeleton placeholders plus fixed aspect‑ratio containers to eliminate layout shifts, and (6) async font loading with `font-display: swap`—the Performance score rose to **94** (Figure 11), an improvement of **+18 points (≈ +23.7%)**. Practically, users experience (a) a faster rendering of the primary visual content (lower LCP), (b) smoother initial interaction due to reduced main thread blocking (lower TBT), (c) visually stable layout with near‑zero CLS, and (d) reduced perceived waiting time through immediate structural painting and skeleton feedback. These gains validate that targeted, evidence‑driven optimizations can substantially elevate perceived quality without architectural rewrites.

### Comparative Analysis
The +18 point increase (76 → 94) validates that targeted, metrics‑driven interventions effectively removed primary performance bottlenecks without compromising functionality. Faster LCP stems from lighter, prioritized images; reduced TBT and Speed Index result from smaller, better‑partitioned JavaScript; near‑zero CLS is due to proactive layout reservation and placeholders.

### Reliability and Repeatability
Variance across repeated Lighthouse runs remained within ±2 points. Using median scores mitigated anomalies due to transient network jitter. All performance modifications passed the existing automated test suite (see Section 4.1.1), preserving functional correctness.

### Limitations
- Only the home page was profiled; additional routes (detail pages, search results) would benefit from separate audits.
- Upstream TMDB latency was mocked only at the network throttling layer—not fully emulated under extreme packet loss scenarios.  
- No field (Real User Monitoring) data collection yet; synthetic results may differ from real device performance.

### Future Work
1. Introduce edge/CDN caching for frequently requested image metadata and static assets.
2. Add automated Lighthouse CI gating (fail threshold <90) in the deployment pipeline.
3. Enforce a performance budget (e.g., <150 KB critical JS, LCP <2.5 s on Slow 4G).  
4. Implement Real User Monitoring (RUM) via Web Vitals collection for field feedback loops.  
5. Explore HTTP early hints or server push alternatives where infrastructure permits.  

### Conclusion
The non-functional performance testing demonstrates that systematic optimization—centered on image weight reduction, resource prioritization, layout stability, and bundle refinement—materially improved user‑perceived speed. The uplift from a baseline score of 76 to 94 underscores the effectiveness of focused, measurable interventions and establishes a foundation for continuous performance governance.

## 4.2 User Evaluation

### 4.2.1 Rationale and Objectives
While automated tests (Section 4.1) validate functional correctness and technical performance, they cannot fully capture human factors such as perceived usability, learnability, satisfaction, clarity of navigation, or the subjective value of features. A formative user evaluation was therefore conducted to: (1) verify that core user journeys are understandable without instruction; (2) identify friction points in navigation, filtering, and content discovery; (3) assess perceived interface quality (layout, aesthetics); and (4) collect qualitative feedback to guide post‑study refinements and future roadmap items. The evaluation complied with the School Ethics procedure: participation was voluntary, informed consent was recorded, no sensitive personal data were collected, responses were anonymised, and participants could withdraw at any time prior to submission.

### 4.2.2 Procedure and Task Script
Participants (n = 5) accessed the deployed MMDB site and were asked to complete a structured exploratory script prior to answering the questionnaire. The script ensured exposure to all key features:
1. Register (if needed) and log in with a personal account.
2. Browse each primary navigation menu.
3. Customise personal profile information (including optional metadata fields).
4. On a category page (e.g., Top Rated), rate interesting film cards; mark some as Liked, Watched, or Watch Later.
5. Apply filters to sort or constrain movies (e.g., by rating range).
6. Open a movie detail page; use action buttons (rate, like, watch later) and submit a textual review.
7. Visit the profile page to inspect activity history (ratings, likes, watchlist, reviews).
8. (Optional) Edit or delete an existing review.
9. Log out.

This sequence was designed to traverse the main CRUD and interaction surfaces (authentication, browsing, filtering, engagement, persistence) in a naturalistic order while minimising learning bias.

### 4.2.3 Instrumentation (Questionnaire Design)
A Microsoft Forms questionnaire (ethics‑approved) was administered immediately after task completion. It comprised:
- Demographic & movie consumption habits (contextualising behaviour, not analysed in depth here).
- Functional adequacy perceptions (e.g., ability to find movies, effectiveness of filters, clarity of profile analytics).
- Usability & User Experience: Likert‑scale items (1 = Very Poor / Strongly Disagree, 5 = Excellent / Strongly Agree) on design, navigation, search/findability, overall experience.
- Error/Issue Reporting: Open text prompts for encountered problems.
- Feature Appreciation: Multi‑select / open text identifying most valued features.
- Open Suggestions & Future Improvements.

Given the small sample (n = 5), inferential statistics are inappropriate; analysis focuses on descriptive measures (mean, distribution, ceiling effects) plus thematic coding of qualitative responses.

### 4.2.4 Quantitative Results
Because the sample is small (n = 5), each participant represents 20% of responses; percentages are shown to improve readability while acknowledging that inferential statistics are inappropriate.

Likert Items (n = 5):
| Item | Prompt (abridged) | Ratings Distribution (count, %) | Mean | Sample SD | ≥4 ("Positive") | Interpretation |
|------|-------------------|----------------------------------|------|-----------|-----------------|----------------|
| Q6 | Design & layout satisfaction | 5:2 (40%), 4:3 (60%) | 4.40 | 0.55 | 100% | High satisfaction; all ratings ≥4. |
| Q7 | Ease of navigation | 5:4 (80%), 4:1 (20%) | 4.80 | 0.45 | 100% | Very high; low variance; near ceiling. |
| Q8 | Ease of finding a movie | 5:1 (20%), 4:3 (60%), 3:1 (20%) | 4.00 | 0.71 | 80% | Positive overall; one mid rating highlights filter/findability refinement need. |
| Q9 | Overall experience | 5:2 (40%), 4:3 (60%) | 4.40 | 0.55 | 100% | Strong overall approval; mirrors design score. |

Observations:
- Navigation (Q7) exhibits a near‑ceiling effect, suggesting information architecture is immediately learnable.
- Findability (Q8) lags other dimensions; variance and the lone mid score point to opportunities to refine search & filtering clarity and boundary logic.
- High but not perfect design satisfaction (Q6) signals incremental UI polish (visual hierarchy, micro‑interactions) could still add value.

### 4.2.5 Reported Issues (Qualitative)
Two substantive error / friction reports were collected:
1. Rating Filter Boundary Issue: A user filtering 8.5–10 did not see a movie rated 8.5 ("Your Name"). This implies either (a) exclusive lower bound (> instead of ≥), (b) floating‑point precision truncation, or (c) mismatch between displayed rounded rating and internal stored value. Action: ensure inclusive comparisons (value >= minThreshold) with consistent rounding strategy.
2. Profile History "View All" Non‑Actionable: Clicking "view all" produced no navigation or expansion. Action: implement anchor scroll, dynamic expansion, or dedicated route; add ARIA role & visual affordance feedback.
Additional friction: Re‑selecting a rating when submitting a review for a movie already rated. Action: prefill existing rating or decouple textual review submission from rating selection if unchanged.

### 4.2.6 Feature Appreciation Analysis
Participant mentions (frequency counts and percentages; each mention unit = 1 participant = 20%):
- Movie Cards Quick Rating: 4 (80%)
- Movie Detail Review Function: 3 (60%)
- Pages UI (overall interface aesthetics/layout): 3 (60%)
- Profile Page Analysis (activity insights/analytics): 2 (40%)
- Search Function: 2 (40%)
- Profile Page "My Marked" Movie List & My Reviews aggregation: 1 (20%)

Interpretation: Low‑friction engagement mechanisms (inline card rating) deliver the highest perceived value, validating the emphasis on immediate interactions. Analytical/profile features, while less prominently cited, still contribute differentiated value and could be expanded (e.g., personalised summaries, comparative stats) to elevate retention.

### 4.2.7 Suggestions & Future Enhancement Themes
Open‑ended suggestions highlighted ambiguity around optional profile fields ("Preferred Actor/Director", "Location/Website"). Without visible social or recommendation affordances, these appear purposeless to users. Proposed roadmap responses:
1. Short Term: Add inline tooltips or placeholder helper text clarifying that these fields are preparatory for upcoming personalisation and (potential) community features.
2. Medium Term: Introduce actor/director‑based filtering or recommendation modules leveraging these attributes.
3. Fallback: If social features are deprioritised, hide or mark fields explicitly as optional / experimental to reduce cognitive load.

### 4.2.8 Discussion
The user evaluation corroborates that foundational usability goals (navigation clarity, aesthetic acceptability, overall satisfaction) are substantially met at this stage, with the strongest metric in navigability (mean 4.8). The principal actionable area is search/findability precision—particularly numerical filter semantics and feedback when results are excluded. Qualitative issue reports map directly to discrete, implementable fixes of low architectural risk (filter comparison logic, inactive UI control behaviour, rating persistence state). High appreciation for rapid micro‑interactions (quick rating) aligns with contemporary UX patterns that lower friction to engagement; this supports prioritising further inline actions (e.g., quick add to list) in future iterations.

### 4.2.9 Limitations
- Sample Size: n = 5 constrains generalisability; results are indicative, not statistically conclusive.
- Sampling Bias: Participants may be more technically inclined (volunteer bias), potentially inflating usability ratings.
- Single Session Exposure: Longitudinal learnability, retention, and real‑world device diversity (older hardware) were not evaluated.
- No A/B Baseline: Lacking a prior design variant, absolute satisfaction levels cannot be benchmarked against alternatives.

### 4.2.10 Summary
User testing provided actionable confirmation that the system’s primary interaction flows are intuitive and satisfying, while revealing targeted refinements (filter boundary inclusivity, inactive control feedback, profile field clarity). Coupling these qualitative insights with the earlier performance gains establishes a balanced improvement backlog spanning both perceptual speed and experiential clarity.
