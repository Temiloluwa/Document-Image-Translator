import React from "react";

import Navbar from "@/components/app/main-area/Navbar";
import PreviewArea from "@/components/app/main-area/PreviewArea";

export default function MainArea() {
  return (
    <main className="flex-1 flex flex-col w-full min-h-0 max-h-full overflow-y-auto">{/* min-h-0 and max-h-full ensure proper flex shrink/grow, overflow-y-auto enables scrolling */}
      <Navbar />
      <div className="px-2 sm:px-4 md:px-6 pb-0 flex flex-col flex-1 w-full min-h-0 max-h-full">
        <div className="mt-2 md:mt-6 flex-1 w-full min-h-0 max-h-full overflow-y-auto">{/* This ensures PreviewArea can scroll if needed */}
          <PreviewArea />
        </div>
      </div>
    </main>
  );
}
