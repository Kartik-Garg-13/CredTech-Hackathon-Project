import faqData from "../../data/FAQdata.js"
import { useState } from "react";

function FAQ() {
  const [openFAQ, setOpenFAQ] = useState(null);

    return(
    <div className="mx-1 space-y-1 min-w-[100%] items-center py-10 flex flex-col bg-gray-100">
    <h1 className="text-center text-xl font-bold md:text-4xl mb-10 py-3 w-[30rem] border-amber-700 border-b-3 ">Frequently Asked Questions</h1>
      {faqData.map((faq) => (
        <div key={faq.id}
          className="overflow-hidden rounded-4xl border border-white/10 bg-gray-300 backdrop-blur-sm transition-all duration-300 hover:bg-black/40 max-w-[80vw]"
          onMouseEnter={() => setOpenFAQ(faq.id)}
          onMouseLeave={() => setOpenFAQ(null)}
        >
          <div className="text-offwhite flex h-[clamp(3.3rem,6vw,6rem)] w-full cursor-pointer items-center justify-center px-8 py-6 text-left transition-colors duration-200 hover:bg-white/5">
            <span className="text-center text-[clamp(0.65rem,1.3vw,1.3rem)] font-bold tracking-tight">
              {faq.question}
            </span>
            <div
              className={`transition-all duration-500 ease-in-out ${
                openFAQ === faq.id ? "rotate-45" : "rotate-0"
              }`}
            ></div>
          </div>

          <div
            className={`overflow-hidden transition-all duration-700 ease-in-out ${
              openFAQ === faq.id
                ? "max-h-60 translate-y-0 opacity-100"
                : "max-h-0 -translate-y-2 opacity-0"
            }`}
            style={{
              transitionProperty: "max-height, opacity, transform",
            }}
          >
            <div className="px-8 pb-6">
              <div className="border-t border-white/10 pt-4">
                <p className="text-offwhite/80 transform text-center text-[clamp(0.65rem,1.3vw,1.3rem)] leading-relaxed transition-transform duration-300">
                  {faq.answer}
                </p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
export default FAQ;