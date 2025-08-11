////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
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

#include "EVI/Type.hpp"

#include "EVI/CKKSTypes.hpp"
#include "EVI/Context.hpp"
#include "EVI/IndexImpl.hpp"
#include "EVI/KeyPack.hpp"
#include "utils/CheckMacros.hpp"
#include "utils/CudaUtils.hpp"
#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"
#include <cstdint>
#include <iostream>
#include <memory>
#include <optional>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <variant>
#include <vector>

namespace evi {

class IndexImpl {
public:
    virtual ~IndexImpl() = default;
    virtual void setData(Blob data, std::optional<KeyPack> = std::nullopt) = 0;
    // virtual void setData(std::vector<DataState> data) = 0;
    virtual void store(const std::string &dir_path) = 0;
    virtual void load(const std::string &dir_path) = 0;
    virtual void serializeTo(std::ostream &stream) = 0;
    virtual void deserializeFrom(std::istream &stream) = 0;
    virtual polydata getPolyData(const int pos, const int level, std::optional<int> vec_idx = std::nullopt,
                                 std::optional<int> idx = std::nullopt) = 0;

    virtual std::vector<int> &getBatchListOfDeviceId(const int device_id) const = 0;
    virtual bool isLoadedToGPU(const int device_id) const = 0;
    virtual u32 getItemCount() const = 0;
    virtual const DataType &getDataType() const = 0;

    virtual void append(const Query item) = 0;

    virtual int getLevel() const = 0;
    virtual u32 getPadRank() const = 0;
    virtual u32 getShowRank() const = 0;
};

template <DeviceType D, DataType T, EvalMode M>
class IndexAdapter : public IndexImpl {
    using EvalImpl = std::conditional_t<!(CHECK_RHOMBUS(M)), std::shared_ptr<IndexBase<D, T, M>>,
                                        std::vector<std::shared_ptr<IndexBase<D, T, M>>>>;
    EvalImpl impl_;
    u32 show_rank_;
    u32 num_impl_;
    u32 num_db_;
    const DataType dtype_;

    // void toSharedA(Evalimpl) const override;

public:
    IndexAdapter(const evi::Context &context);

    void setData(Blob data, std::optional<KeyPack> = std::nullopt) override;
    // void setData(std::vector<DataState> data) override;
    void store(const std::string &dir_path) override;
    void load(const std::string &dir_path) override;
    void serializeTo(std::ostream &stream) override;
    void deserializeFrom(std::istream &stream) override;
    polydata getPolyData(const int pos, const int level, std::optional<int> vec_idx = std::nullopt,
                         std::optional<int> idx = std::nullopt) override;

    void append(const Query item) override;
    bool isLoadedToGPU(const int device_id) const override;
    std::vector<int> &getBatchListOfDeviceId(const int device_id) const override;
    const DataType &getDataType() const override;

    u32 getItemCount() const override;
    int getLevel() const override;
    u32 getPadRank() const override;
    u32 getShowRank() const override {
        return show_rank_;
    }

    // void append(const std::vector<Query> items) override;
};

using Index = std::shared_ptr<IndexImpl>;

Index makeIndex(const Context &context, evi::DataType dtype = DataType::CIPHER);

} // namespace evi
