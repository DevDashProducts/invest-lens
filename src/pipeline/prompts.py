# Analysis prompts for different sections
EXECUTIVE_SUMMARY_PROMPT = """Draft an Executive Summary for the Investment Committee meeting based on the provided information: {{input}}. Adhere strictly to the structure and formatting guidelines outlined below. Avoid unnecessary text, introductory phrases, or deviations from the specified format.  

1. **Transaction Overview**:  
   - State the target company's name, location, and industry focus.  
   - Specify the deal type (e.g., majority acquisition) and transaction value, including components such as upfront payment, performance-based earnouts, and other considerations.  
   - Include any relevant transaction timelines.  

2. **Strategic Rationale**:  
   - Explain the strategic alignment of the acquisition with organizational objectives.  
   - Highlight unique features of the target company, such as proprietary technology, market position, or future growth potential.  
   - Describe synergies with the existing portfolio or operations.  

3. **Key Investment Highlights**:  
   - Summarize core financial metrics (e.g., revenue, growth rates, gross margins) and compare them with industry benchmarks.  
   - Include details on market potential, total addressable market (TAM), and competitive positioning.  
   - Mention any notable operational, product, or customer metrics.  

4. **Critical Risks and Mitigants**:  
   - Identify major risks associated with the transaction, such as integration challenges, talent retention, or competitive dynamics.  
   - Detail mitigation strategies and planned actions to address these risks.  

5. **Required Actions**:  
   - Outline the next steps, including necessary approvals, due diligence processes, and closing timelines.  

6. **References**:  
   - Provide a numbered list of references for all data points and statements in the format:  
     1. [URL1/Section/Page]  
     2. [URL2/Section/Page]  

**Requirements**:  
hello
- Use clear subheadings and bullet points under each section for readability.  
- Quantify statements with specific metrics and comparative data.  
- Keep the main text within 1000 words, ensuring all exhibits and references are concise.  
- Ensure consistent formatting for smooth integration into a PDF template.  
- Do not include additional information outside the given structure.  
- Use numbered references for each line where applicable eg:[1], ensuring all data points are appropriately sourced.  
- Avoid redundant or fabricated references; only provide unique and valid ones.  
- Ensure the final output adheres strictly to this structure and formatting.  

"""

COMPANY_OVERVIEW_PROMPT = """
Draft a detailed company overview section using the provided information: {{input}}. Follow the structure and formatting guidelines strictly. Avoid adding unnecessary text or introductory phrases. Use the format below:  

1. **Company Introduction**:  
   - Briefly describe the company's history and evolution.  
   - Summarize the current business focus and mission statement.  
   - Include key operational metrics, such as annual revenue, employee count, and number of operational locations.  

2. **Business Model**:  
   - Explain the company's core value proposition.  
   - List and describe primary revenue streams and their significance.  
   - Highlight major partnerships and key business relationships.  
   - Provide an overview of cost structure and profit margins.  

3. **Products and Services**:  
   - List the company’s primary product or service offerings.  
   - Highlight distinctive features and competitive advantages.  
   - Describe the company’s technology, intellectual property, and R&D efforts.  
   - Include any details on planned future products or service enhancements.  

4. **Market Position**:  
   - Define the company’s target market segments and customer demographics.  
   - Include data on market share and industry rankings.  
   - Provide a competitive analysis and comparisons with key competitors.  
   - Highlight the company’s competitive advantages with supporting examples.  

5. **Operations Overview**:  
   - Summarize the company’s geographic reach and market coverage.  
   - Outline production or service delivery capabilities.  
   - Describe quality assurance measures and relevant certifications.  
   - Include operational metrics, such as production volume or service efficiency.  

6. **Management and Organization**:  
   - Provide a summary of the leadership team and their professional backgrounds.  
   - Describe the organization structure and key functional areas.  
   - Highlight employee expertise, skills, and key team dynamics.  

7. **References**:  
   - Include a numbered list of references for all data and statements. Example:  
      1. URL1/Section/Page  
      2. URL2/Section/Page  

**Requirements**:  
- Use clear subheadings and bullet points for each section.  
- Quantify all information with specific metrics and comparisons.  
- Include industry benchmarks or competitor data where relevant.  
- Ensure the content is concise and professional, with a word limit of 1000 words.  
- Maintain consistent formatting for PDF integration.  
- Do not include redundant information, fabricated references, or content outside the specified structure.  
- Ensure references are unique and presented in the correct format, such as [1] or [2].  
- Stick strictly to the specified format without adding introductory phrases or additional text.  

"""

FINANCIAL_OVERVIEW_PROMPT = """
Draft a detailed financial overview section using the provided information: {{input}}. Follow the structure and formatting guidelines strictly. Use the format below:  

1. **Financial Highlights**:  
   - Summarize key revenue trends and growth metrics.  
   - Highlight profitability indicators such as gross margins, operating margins, and net income.  
   - Include key financial performance indicators like EBITDA, ROE, and ROA.  
   - Note any significant financial developments, such as mergers, acquisitions, or large contracts.  

2. **Historical Performance Analysis**:  
   - Provide revenue breakdown by product, service, or geography.  
   - Discuss trends in cost structure, including fixed versus variable costs.  
   - Analyze changes in gross, operating, and net margins over time.  
   - Highlight the role of operating leverage in performance trends.  

3. **Balance Sheet Overview**:  
   - Summarize the company’s asset base, including fixed, current, and intangible assets.  
   - Provide working capital metrics such as receivables, payables, and inventory levels.  
   - Describe the company’s capital structure, including the debt-to-equity ratio.  
   - Outline liquidity positions, including cash reserves and key ratios like the current ratio.  

4. **Cash Flow Analysis**:  
   - Discuss operating cash flow trends and drivers.  
   - Highlight capital expenditures and their implications on growth or maintenance.  
   - Summarize free cash flow generation and utilization.  
   - Include key cash conversion metrics, such as the cash conversion cycle.  

5. **Key Operating Metrics**:  
   - Present unit economics such as revenue per unit or cost per unit.  
   - Include customer-centric metrics, such as churn rate and customer lifetime value (CLV).  
   - Highlight operational efficiency ratios, including asset turnover and inventory turnover.  
   - Provide relevant industry-specific key performance indicators (KPIs).  

6. **Financial Projections**:  
   - Outline growth projections based on market trends and company initiatives.  
   - Include expectations for gross, operating, and net margins.  
   - Summarize planned capital expenditures and funding requirements.  
   - Highlight key drivers and risks that could influence financial forecasts.  

7. **References**:  
   - Include a numbered list of all references cited in the text. Example:  
      1. URL1/Section/Page  
      2. URL2/Section/Page  

**Requirements**:  
- Use clear subheadings and bullet points for all sections.  
- Quantify all data with specific metrics, including comparisons to industry averages or competitor benchmarks.  
- Emphasize year-over-year trends and variances where applicable.  
- Limit content to 1000 words and ensure all data is concise and professionally presented.  
- Maintain a consistent and structured format for seamless PDF integration.  
- Avoid redundant information, fabricated references, or content outside the specified structure.  
- References should be unique and cited appropriately using [1], [2], etc.  
- Stick to the given format without adding additional text, introductory phrases, or warnings.  
"""
