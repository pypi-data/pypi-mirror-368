////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
//                                                                            //
// This software and/or source code may be commercially used and/or           //
// disseminated only with the written permission of CryptoLab Inc,            //
// or in accordance with the terms and conditions stipulated in the           //
// agreement/contract under which the software and/or source code has been    //
// supplied by CryptoLab Inc. Any unauthorized commercial use and/or          //
// dissemination of this file is strictly prohibited and will constitute      //
// an infringement of copyright.                                              //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "CKKSTypes.hpp"
#include "EVI/Basic.cuh"
#include "EVI/CKKSTypes.hpp"
#include "EVI/Context.hpp"
#include "EVI/KeyPack.hpp"
#include "EVI/Type.hpp"
#include "utils/Exceptions.hpp"
#include "utils/span.hpp"

#include <cstdint>
#include <functional>
#include <optional>
#include <string>
#include <utility>
#include <vector>

#ifdef BUILD_WITH_HEAAN
#include "Cleaner/Cleaner.hpp"
#include "HEaaN/Ciphertext.hpp"
#include "HEaaN/Decryptor.hpp"
#include "HEaaN/Message.hpp"
#include "HEaaN/ParameterPreset.hpp"
#endif

namespace evi {

class DecryptorImpl {
public:
    explicit DecryptorImpl(const evi::Context &context);

    Message decrypt(const SearchResult ctxt, const evi::SecretKey &key, bool is_score,
                    std::optional<double> scale = std::nullopt);
    Message decrypt(const SearchResult ctxt, const std::string &key_path, bool is_score,
                    std::optional<double> scale = std::nullopt);

    Message decrypt(const Query ctxt, const evi::SecretKey &key, std::optional<double> scale = std::nullopt);
    Message decrypt(const Query ctxt, const std::string &key_path, std::optional<double> scale = std::nullopt);

#ifdef BUILD_WITH_HEAAN
    explicit DecryptorImpl(const std::string &path);

    void decrypt(const HEaaN::Ciphertext &ctxt, HEaaN::Message &dmsg);

    std::optional<HEaaN::Context> heaan_context_;
    std::shared_ptr<HEaaN::Decryptor> heaan_dec_;
    std::shared_ptr<HEaaN::SecretKey> heaan_sk_;
    std::shared_ptr<HEaaN::Cleaner> heaan_cleaner_;

    std::shared_ptr<HEaaN::Cleaner> getCleaner() {
        return heaan_cleaner_;
    }

    HEaaN::Context &getHEaaNContext() {
        return heaan_context_.value();
    }

#endif

private:
    const evi::Context context_;
};

using Decryptor = std::shared_ptr<DecryptorImpl>;

Decryptor makeDecryptor(const evi::Context &context);

#ifdef BUILD_WITH_HEAAN
Decryptor makeDecryptor(const std::string &path);
#endif

} // namespace evi
