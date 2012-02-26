#include <llvm/LLVMContext.h>
#include <llvm/Module.h>
#include <llvm/DerivedTypes.h>
#include <llvm/Constants.h>
#include <llvm/Instructions.h>
#include <llvm/Bitcode/ReaderWriter.h>
#include <llvm/Analysis/DebugInfo.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/ADT/StringSet.h>
#include <llvm/Pass.h>
#include <llvm/Function.h>
#include <iostream>
#include <llvm/Support/raw_ostream.h>

using namespace llvm;

namespace {

struct AbstractInterpretation : public ModulePass {
  static char ID;

  AbstractInterpretation()
    : ModulePass(ID) {
  }

  void getContextName(DIDescriptor Context, std::string &N) {
    if (Context.isNameSpace()) {
      DINameSpace NS(Context);
      if (!NS.getName().empty()) {
        getContextName(NS.getContext(), N);
        N = N + NS.getName().str() + "::";
      }
    } else if (Context.isType()) {
      DIType TY(Context);
      if (!TY.getName().empty()) {
        getContextName(TY.getContext(), N);
        N = N + TY.getName().str() + "::";
      }
    }
  }

  virtual bool runOnModule(Module &M) {
    StringSet<> Processed;
    if (NamedMDNode *NMD = M.getNamedMetadata("llvm.dbg.sp"))
      for (unsigned i = 0, e = NMD->getNumOperands(); i != e; ++i) {
        std::string Name;
        DISubprogram SP(NMD->getOperand(i));
        if (SP.Verify())
          getContextName(SP.getContext(), Name);
        Name = Name + SP.getDisplayName().str();
        if (!Name.empty() && Processed.insert(Name)) {
	  std::cout << Name << "\n";
        }
      }
    return false;
  }

  virtual void getAnalysisUsage(AnalysisUsage &AU) const {
    AU.setPreservesAll();
  }
};

char AbstractInterpretation::ID = 0;

}

static RegisterPass<AbstractInterpretation> X("abstract-interpretation",
					      "Abstract Interpretation Pass",
					      false /* Only looks at CFG */,
					      false /* Analysis Pass */);
